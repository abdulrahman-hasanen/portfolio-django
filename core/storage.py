import uuid
from pathlib import PurePosixPath

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import NotFound
from django.core.files.storage import Storage


class CloudinaryMediaStorage(Storage):
    """
    Store uploaded project images in Cloudinary.
    The database stores the Cloudinary public ID and format.
    """

    def get_available_name(self, name, max_length=None):
        path = PurePosixPath(name)

        directory = "" if str(path.parent) == "." else f"{path.parent.as_posix()}/"

        extension = path.suffix.lower()
        unique_suffix = uuid.uuid4().hex[:12]

        max_stem_length = (
            max_length - len(directory) - len(extension) - len(unique_suffix) - 1
            if max_length
            else len(path.stem)
        )

        if max_stem_length < 1:
            from django.core.exceptions import SuspiciousFileOperation

            raise SuspiciousFileOperation("The uploaded filename is too long.")

        stem = path.stem[:max_stem_length]
        return f"{directory}{stem}-{unique_suffix}{extension}"

    def _save(self, name, content):
        path = PurePosixPath(name)
        public_id = path.with_suffix("").as_posix()

        if hasattr(content, "seek"):
            content.seek(0)

        content.name = path.name

        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
        )

        uploaded_public_id = result["public_id"]
        image_format = result.get("format") or "webp"

        return f"{uploaded_public_id}.{image_format}"

    def url(self, name):
        path = PurePosixPath(name)
        public_id = path.with_suffix("").as_posix()
        image_format = path.suffix.lstrip(".") or "webp"

        return cloudinary.CloudinaryImage(public_id).build_url(
            secure=True,
            format=image_format,
        )

    def exists(self, name):
        path = PurePosixPath(name)
        public_id = path.with_suffix("").as_posix()

        try:
            cloudinary.api.resource(
                public_id,
                resource_type="image",
            )
            return True
        except NotFound:
            return False

    def delete(self, name):
        path = PurePosixPath(name)
        public_id = path.with_suffix("").as_posix()

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True,
        )

    def size(self, name):
        path = PurePosixPath(name)
        public_id = path.with_suffix("").as_posix()

        result = cloudinary.api.resource(
            public_id,
            resource_type="image",
        )

        return result["bytes"]
