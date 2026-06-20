from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent.parent.parent


class AvatarConfig(BaseModel):
    allowed_types: set[str] = {"jpeg", "png", "webp"}
    max_file_size: int = 5 * 1024 * 1024


class AttachmentConfig(BaseModel):
    allowed_mime_types: set[str] = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "text/plain",
        "text/csv",
    }
    max_file_size: int = 20 * 1024 * 1024


class UploadsConfig(BaseModel):
    base_dir: Path = BASE_DIR / "uploads"
    avatar: AvatarConfig = AvatarConfig()
    attachment: AttachmentConfig = AttachmentConfig()

    @property
    def avatars_dir(self) -> Path:
        return self.base_dir / "avatars"

    @property
    def default_avatar(self) -> Path:
        return self.base_dir / "avatars" / "default.png"

    @property
    def org_avatars_dir(self) -> Path:
        return self.base_dir / "org_avatars"

    def org_avatar_path(self, org_id) -> Path:
        return self.org_avatars_dir / str(org_id) / "avatar"

    def attachment_path(
        self,
        org_id,
        project_id,
        task_id,
        attachment_id,
    ) -> Path:
        return (
            self.base_dir
            / "attachments"
            / str(org_id)
            / str(project_id)
            / str(task_id)
            / str(attachment_id)
        )
