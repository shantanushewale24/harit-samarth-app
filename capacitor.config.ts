import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'app.lovable.438158a80f0749989593b1094e419f2f',
  appName: 'Agri bio',
  webDir: 'dist',
  server: {
    url: 'https://438158a8-0f07-4998-9593-b1094e419f2f.lovableproject.com?forceHideBadge=true',
    cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#22c55e",
      showSpinner: false
    }
  }
};

export default config;
