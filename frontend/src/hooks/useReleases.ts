import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { releasesApi } from "../api/releasesApi";
import { qk } from "../lib/queryKeys";
import type { ReleaseCreate } from "../types/release";

export function useReleases() {
  return useQuery({ queryKey: qk.releases, queryFn: releasesApi.list });
}

export function useCreateRelease() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReleaseCreate) => releasesApi.create(payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.releases });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
