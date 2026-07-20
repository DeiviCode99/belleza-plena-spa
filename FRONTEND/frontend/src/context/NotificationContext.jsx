import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../lib/axiosClient';

const NotificationContext = createContext(null);

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

export function NotificationProvider({ children }) {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [swRegistration, setSwRegistration] = useState(null);

  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      navigator.serviceWorker.ready.then(setSwRegistration).catch(() => {});
    }
  }, []);

  const getVapidPublicKey = useCallback(async () => {
    try {
      const { data } = await api.get('push/public-key/');
      return data.publicKey;
    } catch {
      return null;
    }
  }, []);

  const subscribe = useCallback(async () => {
    if (!swRegistration) return;
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') return;

      const publicKey = await getVapidPublicKey();
      if (!publicKey) return;

      const subscription = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
      });

      await api.post('push/subscribe/', subscription.toJSON());
      setIsSubscribed(true);
    } catch (err) {
      console.error('Push subscription failed:', err);
    }
  }, [swRegistration, getVapidPublicKey]);

  const unsubscribe = useCallback(async () => {
    if (!swRegistration) return;
    try {
      const subscription = await swRegistration.pushManager.getSubscription();
      if (subscription) {
        await api.post('push/unsubscribe/', { endpoint: subscription.endpoint });
        await subscription.unsubscribe();
      }
      setIsSubscribed(false);
    } catch (err) {
      console.error('Push unsubscribe failed:', err);
    }
  }, [swRegistration]);

  useEffect(() => {
    if (!swRegistration) return;
    swRegistration.pushManager.getSubscription().then((sub) => {
      setIsSubscribed(!!sub);
    });
  }, [swRegistration]);

  return (
    <NotificationContext.Provider value={{ isSubscribed, subscribe, unsubscribe }}>
      {children}
    </NotificationContext.Provider>
  );
}

export const useNotification = () => useContext(NotificationContext);
