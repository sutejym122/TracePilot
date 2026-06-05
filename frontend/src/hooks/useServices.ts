import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { servicesApi } from "../api/servicesApi";
import { qk } from "../lib/queryKeys";
import type { ServiceCreate } from "../types/service";

export function useServices() {
  return useQuery({ queryKey: qk.services, queryFn: servicesApi.list });
}

export function useCreateService() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: ServiceCreate) => servicesApi.create(payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.services });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
