import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { healthApi } from "../api/healthApi";
import { metricsApi } from "../api/metricsApi";
import { servicesApi } from "../api/servicesApi";
import { qk } from "../lib/queryKeys";
import type { ApiMetricCreate } from "../types/metric";

export function useService(id: string) {
  return useQuery({
    queryKey: qk.service(id),
    queryFn: () => servicesApi.get(id),
  });
}

export function useServiceHealth(id: string) {
  return useQuery({
    queryKey: qk.serviceHealth(id),
    queryFn: () => healthApi.list(id),
  });
}

export function useServiceMetrics(id: string) {
  return useQuery({
    queryKey: qk.serviceMetrics(id),
    queryFn: () => metricsApi.list(id),
  });
}

export function useRunHealthCheck(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => healthApi.runCheck(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.serviceHealth(id) });
      client.invalidateQueries({ queryKey: qk.service(id) }); // status is denormalized
      client.invalidateQueries({ queryKey: qk.services });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useSimulateMetric(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => metricsApi.simulate(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.serviceMetrics(id) });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useCreateMetric(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: ApiMetricCreate) => metricsApi.create(id, payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.serviceMetrics(id) });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}

export function useDeleteService(id: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => servicesApi.remove(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: qk.services });
      client.invalidateQueries({ queryKey: qk.dashboard });
    },
  });
}
