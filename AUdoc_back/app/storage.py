"""
Supabase Storage utility for uploading and managing media files.

Handles doctor profile photos and any other media that needs to persist
across Render deployments by storing them in Supabase Storage.

Falls back to local file storage when Supabase credentials are not configured
(e.g., during local development).
"""

import os
import uuid
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _supabase_is_configured():
    """Check if Supabase Storage credentials are properly set."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    return bool(url and key and "YOUR_" not in key)


def _get_supabase_client():
    """Lazy-initialise and return the Supabase client."""
    try:
        from supabase import create_client
    except ImportError:
        logger.error("supabase package not installed. Run: pip install supabase")
        return None

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    return create_client(url, key)


def _upload_to_local(image_file):
    """
    Save an uploaded image to the local media directory (for development).

    Returns the URL path that Django can serve via MEDIA_URL.
    """
    doctors_dir = os.path.join(settings.MEDIA_ROOT, "doctors")
    os.makedirs(doctors_dir, exist_ok=True)

    ext = os.path.splitext(image_file.name)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(doctors_dir, unique_name)

    # Read content and write to disk
    content = image_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Return a URL that the Django dev server can serve
    local_url = f"{settings.MEDIA_URL}doctors/{unique_name}"
    logger.info(f"✅ Saved doctor photo locally: {local_url}")
    return local_url


def _upload_to_supabase(image_file):
    """
    Upload an image to Supabase Storage.

    Returns the public URL of the uploaded image, or None on failure.
    """
    client = _get_supabase_client()
    if client is None:
        return None

    bucket_name = os.environ.get("SUPABASE_STORAGE_BUCKET", "media")
    ext = os.path.splitext(image_file.name)[1] or ".jpg"
    unique_name = f"doctors/{uuid.uuid4().hex}{ext}"

    try:
        file_content = image_file.read()
        content_type = getattr(image_file, 'content_type', 'image/jpeg')

        client.storage.from_(bucket_name).upload(
            path=unique_name,
            file=file_content,
            file_options={"content-type": content_type},
        )

        public_url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/{bucket_name}/{unique_name}"
        logger.info(f"✅ Uploaded doctor photo to Supabase: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"❌ Failed to upload doctor photo to Supabase: {e}")
        return None


def upload_doctor_photo(image_file):
    """
    Upload a doctor profile photo.

    Uses Supabase Storage if configured, otherwise saves to local media folder.

    Args:
        image_file: A Django UploadedFile (already validated/processed).

    Returns:
        str: The URL of the uploaded image.
    """
    if _supabase_is_configured():
        url = _upload_to_supabase(image_file)
        if url:
            return url
        logger.warning("Supabase upload failed, falling back to local storage.")

    return _upload_to_local(image_file)


def delete_doctor_photo(photo_url):
    """
    Delete a doctor photo. Handles both Supabase and local URLs.

    Args:
        photo_url: The URL of the photo to delete.
    """
    if not photo_url:
        return

    # Check if it's a Supabase URL
    supabase_url = os.environ.get("SUPABASE_URL", "")
    if supabase_url and photo_url.startswith(supabase_url):
        _delete_from_supabase(photo_url)
    elif photo_url.startswith(settings.MEDIA_URL):
        _delete_from_local(photo_url)


def _delete_from_supabase(photo_url):
    """Delete a photo from Supabase Storage by its public URL."""
    client = _get_supabase_client()
    if client is None:
        return

    bucket_name = os.environ.get("SUPABASE_STORAGE_BUCKET", "media")

    try:
        marker = f"/storage/v1/object/public/{bucket_name}/"
        if marker in photo_url:
            file_path = photo_url.split(marker, 1)[1]
            client.storage.from_(bucket_name).remove([file_path])
            logger.info(f"🗑️ Deleted old doctor photo from Supabase: {file_path}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete old doctor photo from Supabase: {e}")


def _delete_from_local(photo_url):
    """Delete a photo from the local media directory."""
    try:
        # Convert URL path to filesystem path
        relative_path = photo_url.replace(settings.MEDIA_URL, "", 1)
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Deleted old local doctor photo: {file_path}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete old local doctor photo: {e}")
