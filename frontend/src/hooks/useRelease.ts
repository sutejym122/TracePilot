import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { releasesApi } from "../api/releasesApi";
import { qk } from "../lib/queryKeys";
import type { ChecklistUpdate, ReleaseUpdate } from "../types/release";

export function useRelease(id: string) {
  return useQuery({
    queryKey: qk.release(id),
    queryFn: () => releasesApi.get(id),
  });
}

export function useReleaseChecklist(id: string) {
  return useQuery({
    queryKey: qk.releaseChecklist(id),
    queryFn: () => releasesApi.getChecklist(id),
  });
}

export function useUpdateChecklist(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: ChecklistUpdate) =>
      releasesApi.updateChecklist(id, payload),
    onSuccess: (updated) => {
      // The PATCH response IS the recomputed checklist — seed the cache with it
      // so the score/status update immediately, then invalidate the dashboard.
      client.setQueryData(qk.releaseChecklist(id), updated);
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useUpdateRelease(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReleaseUpdate) => releasesApi.update(id, payload),
    onSuccess: (updated) => {
      client.setQueryData(qk.release(id), updated);
      client.invalidateQueries({ queryKey: qk.releases });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useDeleteRelease(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => releasesApi.remove(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.releases });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
