import os
from PIL import Image


class ConsistencyChecker:
    def __init__(self, base_path="data/sorted"):
        self.base_path = base_path

    # =========================
    # MAIN CHECK
    # =========================

    def run(self):
        print("\n🔍 Running Dataset Consistency Check...\n")

        for bucket in os.listdir(self.base_path):
            bucket_path = os.path.join(self.base_path, bucket)

            if not os.path.isdir(bucket_path):
                continue

            self._check_bucket(bucket, bucket_path)

        print("\n✅ Consistency Check Completed\n")

    # =========================
    # BUCKET CHECK
    # =========================

    def _check_bucket(self, bucket, bucket_path):
        print(f"\n📂 Bucket: {bucket}")

        for resolution in ["256", "512", "1024", "2048"]:
            res_path = os.path.join(bucket_path, resolution)

            if not os.path.exists(res_path):
                print(f"⚠️ Missing folder: {resolution}")
                continue

            files = os.listdir(res_path)
            images = [f for f in files if f.endswith(".jpg")]

            print(f"  {resolution}px → {len(images)} images")

            # run checks
            self._check_pairs(res_path, images)
            self._check_corruption(res_path, images)

    # =========================
    # CHECK JPG ↔ TXT PAIR
    # =========================

    def _check_pairs(self, path, images):
        for img in images:
            txt_file = img.replace(".jpg", ".txt")
            txt_path = os.path.join(path, txt_file)

            if not os.path.exists(txt_path):
                print(f"❌ Missing TXT for {img}")

    # =========================
    # CHECK CORRUPTED IMAGES
    # =========================

    def _check_corruption(self, path, images):
        for img in images:
            img_path = os.path.join(path, img)

            try:
                with Image.open(img_path) as im:
                    im.verify()
            except Exception:
                print(f"❌ Corrupted image: {img}")