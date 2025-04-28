SOFT_IGNORE_PATTERNS = [
    # archives
    "*.7z", "*.zip", "*.tar.*", "*.tgz", "*.rar",
    "*.gz", "*.bz2", "*.xz", "*.zst",

    # binary model/data blobs
    "*.arrow", "*.bin", "*.ckpt", "*.ftz",
    "*.h5", "*.joblib", "*.mlmodel",
    "*.model", "*.msgpack", "*.npy", "*.npz",
    "*.onnx", "*.ot", "*.parquet", "*.pb",
    "*.pickle", "*.pkl", "*.pt", "*.pth",
    "*.safetensors",

    # saved-model folders
    "saved_model/*",

    # audio
    "*.pcm", "*.sam", "*.raw",
    "*.aac", "*.flac", "*.mp3", "*.ogg", "*.wav",

    # images
    "*.bmp", "*.gif", "*.png", "*.tiff",
    "*.jpg", "*.jpeg", "*.webp",

    # TensorBoard events
    "*tfevents*",
]