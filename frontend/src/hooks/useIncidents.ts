import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { incidentsApi } from "../api/incidentsApi";
import { qk } from "../lib/queryKeys";
import type { IncidentCreate } from "../types/incident";

export function useIncidents() {
  return useQuery({ queryKey: qk.incidents, queryFn: incidentsApi.list });
}

export function useCreateIncident() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: IncidentCreate) => incidentsApi.create(payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.incidents });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
