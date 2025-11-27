export async function uploadPhoto(file: File): Promise<string> {
  if (!file) throw new Error("No file provided.");

  if (!file.type.startsWith("image/")) {
    throw new Error("Only image files are allowed.");
  }

  if (file.size > 5 * 1024 * 1024) {
    throw new Error("File size exceeds 5MB limit.");
  }

  // TODO: Integrate with cloud storage (S3, Cloudinary, etc.)
  return `https://placeholder.com/photo_${Date.now()}`;
}
