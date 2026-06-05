import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { incidentsApi } from "../api/incidentsApi";
import { qk } from "../lib/queryKeys";
import type {
  IncidentUpdateCreate,
  IncidentUpdatePayload,
} from "../types/incident";

export function useIncident(id: string) {
  return useQuery({
    queryKey: qk.incident(id),
    queryFn: () => incidentsApi.get(id),
  });
}

export function useIncidentUpdates(id: string) {
  return useQuery({
    queryKey: qk.incidentUpdates(id),
    queryFn: () => incidentsApi.listUpdates(id),
  });
}

export function useAddIncidentUpdate(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: IncidentUpdateCreate) =>
      incidentsApi.addUpdate(id, payload),
    onSuccess: () => {
      // A status-carrying update mutates the parent incident (and maybe
      // resolved_at), so refetch both the timeline and the incident itself.
      client.invalidateQueries({ queryKey: qk.incidentUpdates(id) });
      client.invalidateQueries({ queryKey: qk.incident(id) });
      client.invalidateQueries({ queryKey: qk.incidents });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useUpdateIncident(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: IncidentUpdatePayload) =>
      incidentsApi.update(id, payload),
    onSuccess: (updated) => {
      client.setQueryData(qk.incident(id), updated);
      client.invalidateQueries({ queryKey: qk.incidents });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useDeleteIncident(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => incidentsApi.remove(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.incidents });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
