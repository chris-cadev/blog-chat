interface UmamiEventData {
  [key: string]: string | number | boolean | null | undefined;
}

interface UmamiTrackOptions {
  beacon?: boolean;
}

interface UmamiTracker {
  track: (eventName: string, eventData?: UmamiEventData) => void;
  identify?: (sessionData: Record<string, string>) => void;
}

interface Window {
  umami?: UmamiTracker;
  trackUmami?: (
    eventName: string,
    eventData?: UmamiEventData,
    options?: UmamiTrackOptions
  ) => void;
}
