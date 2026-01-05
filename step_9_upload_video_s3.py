import boto3
import httpx
import uuid
import os

s3_client = boto3.client("s3")


async def upload_kling_video_to_s3(
    kling_video_url: str,
    bucket: str,
    prefix: str = "kling-videos/",
) -> str:
    """
    Downloads Kling video and uploads to S3.
    Returns public S3 URL.
    """

    video_id = f"{uuid.uuid4()}.mp4"
    s3_key = f"{prefix}{video_id}"
    local_path = f"/tmp/{video_id}"

    # 1️⃣ Download video
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.get(kling_video_url)
        resp.raise_for_status()

        with open(local_path, "wb") as f:
            f.write(resp.content)

    # 2️⃣ Upload to S3
    s3_client.upload_file(
        local_path,
        bucket,
        s3_key,
        ExtraArgs={"ContentType": "video/mp4"}
    )

    # 3️⃣ Cleanup
    os.remove(local_path)

    return f"https://{bucket}.s3.amazonaws.com/{s3_key}"
