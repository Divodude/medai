/**
 * Shared location utility.
 * Returns { city, lat, lng } or {} if not available.
 * Caches result in Zustand store to avoid repeated GPS prompts.
 */
import useHealthStore from '../store/useHealthStore';

export async function resolveUserCity() {
  // Return cached location first
  const cached = useHealthStore.getState().userLocation;
  if (cached) return cached;

  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve('');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&format=json`
          );
          const data = await res.json();
          const city =
            data.address?.city ||
            data.address?.town ||
            data.address?.village ||
            data.address?.county ||
            '';
          if (city) {
            useHealthStore.getState().setUserLocation(city);
          }
          resolve(city);
        } catch {
          resolve('');
        }
      },
      () => resolve(''),
      { timeout: 5000 }
    );
  });
}
