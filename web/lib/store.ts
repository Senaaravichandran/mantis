import { create } from "zustand";

interface MantisStore {
  selectedAssetId: string | null;
  setSelectedAssetId: (id: string | null) => void;
  alertCount: number;
  setAlertCount: (count: number) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  mapCenter: [number, number];
  setMapCenter: (center: [number, number]) => void;
}

export const useMantisStore = create<MantisStore>((set) => ({
  selectedAssetId: null,
  setSelectedAssetId: (id) => set({ selectedAssetId: id }),
  alertCount: 0,
  setAlertCount: (count) => set({ alertCount: count }),
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  mapCenter: [-79.9959, 40.4406], // Pittsburgh
  setMapCenter: (center) => set({ mapCenter: center }),
}));
