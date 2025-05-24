from huggingface_hub import snapshot_download
# pip install -U huggingface_hub

if __name__ == "__main__":
    snapshot_download(
        repo_id="GeoGPT-Research-Project/Qwen2.5-72B-GeoGPT",
        resume_download=True,
        local_dir_use_symlinks=False
    )

    # max_workers=2,
    # local_dir="~/.cache/huggingface/hub/models--GeoGPT-Research-Project--Qwen2.5-72B-GeoGPT",
    # local_dir_use_symlinks=False  # vllm need to False
    print("✅ Download complete.")
