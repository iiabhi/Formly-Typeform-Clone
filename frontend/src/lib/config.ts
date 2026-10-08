export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000";

export function shareUrl(slug: string): string {
  return `${APP_URL}/to/${slug}`;
}
