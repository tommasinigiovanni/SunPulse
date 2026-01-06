/**
 * useBuildings Hook
 * 
 * Hook per la gestione degli edifici (CRUD operations)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { axiosInstance } from '../utils/api';
import type {
  Building,
  BuildingListResponse,
  CreateBuildingRequest,
  UpdateBuildingRequest,
  BuildingDevicesResponse,
  BuildingMembersResponse,
  AddDeviceToBuildingRequest,
  InviteMemberRequest,
  UpdateMemberRoleRequest,
} from '../types/building';

// ============================================================================
// Query Keys
// ============================================================================

export const buildingKeys = {
  all: ['buildings'] as const,
  lists: () => [...buildingKeys.all, 'list'] as const,
  list: (filters: string) => [...buildingKeys.lists(), { filters }] as const,
  details: () => [...buildingKeys.all, 'detail'] as const,
  detail: (id: number) => [...buildingKeys.details(), id] as const,
  devices: (id: number) => [...buildingKeys.detail(id), 'devices'] as const,
  members: (id: number) => [...buildingKeys.detail(id), 'members'] as const,
  weather: (id: number) => [...buildingKeys.detail(id), 'weather'] as const,
};

// ============================================================================
// API Functions
// ============================================================================

const fetchBuildings = async (): Promise<Building[]> => {
  const { data } = await axiosInstance.get<BuildingListResponse>('/buildings/');
  return data.buildings;
};

const fetchBuilding = async (id: number): Promise<Building> => {
  const { data } = await axiosInstance.get<Building>(`/buildings/${id}`);
  return data;
};

const createBuilding = async (building: CreateBuildingRequest): Promise<Building> => {
  const { data } = await axiosInstance.post<Building>('/buildings/', building);
  return data;
};

const updateBuilding = async ({ id, ...building }: UpdateBuildingRequest & { id: number }): Promise<Building> => {
  const { data } = await axiosInstance.put<Building>(`/buildings/${id}`, building);
  return data;
};

const deleteBuilding = async (id: number): Promise<void> => {
  await axiosInstance.delete(`/buildings/${id}`);
};

const fetchBuildingDevices = async (buildingId: number) => {
  const { data } = await axiosInstance.get<BuildingDevicesResponse>(`/buildings/${buildingId}/devices`);
  return data.devices;
};

const addDeviceToBuilding = async ({ buildingId, ...device }: AddDeviceToBuildingRequest & { buildingId: number }) => {
  const { data } = await axiosInstance.post(`/buildings/${buildingId}/devices`, device);
  return data;
};

const removeDeviceFromBuilding = async ({ buildingId, deviceId }: { buildingId: number; deviceId: number }) => {
  await axiosInstance.delete(`/buildings/${buildingId}/devices/${deviceId}`);
};

const fetchBuildingMembers = async (buildingId: number) => {
  const { data } = await axiosInstance.get<BuildingMembersResponse>(`/buildings/${buildingId}/members`);
  return data.members;
};

const inviteMember = async ({ buildingId, ...member }: InviteMemberRequest & { buildingId: number }) => {
  const { data } = await axiosInstance.post(`/buildings/${buildingId}/members`, member);
  return data;
};

const updateMemberRole = async ({ buildingId, userId, ...role }: UpdateMemberRoleRequest & { buildingId: number; userId: number }) => {
  const { data } = await axiosInstance.put(`/buildings/${buildingId}/members/${userId}`, role);
  return data;
};

const removeMember = async ({ buildingId, userId }: { buildingId: number; userId: number }) => {
  await axiosInstance.delete(`/buildings/${buildingId}/members/${userId}`);
};

// ============================================================================
// Hooks
// ============================================================================

/**
 * Hook per ottenere la lista di tutti gli edifici dell'utente
 */
export const useBuildings = () => {
  return useQuery({
    queryKey: buildingKeys.lists(),
    queryFn: fetchBuildings,
    staleTime: 5 * 60 * 1000, // 5 minuti
  });
};

/**
 * Hook per ottenere i dettagli di un edificio specifico
 */
export const useBuilding = (id: number) => {
  return useQuery({
    queryKey: buildingKeys.detail(id),
    queryFn: () => fetchBuilding(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Hook per creare un nuovo edificio
 */
export const useCreateBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createBuilding,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.lists() });
    },
  });
};

/**
 * Hook per aggiornare un edificio
 */
export const useUpdateBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateBuilding,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.lists() });
      queryClient.invalidateQueries({ queryKey: buildingKeys.detail(data.id) });
    },
  });
};

/**
 * Hook per eliminare un edificio
 */
export const useDeleteBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteBuilding,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.lists() });
    },
  });
};

/**
 * Hook per ottenere i dispositivi di un edificio
 */
export const useBuildingDevices = (buildingId: number) => {
  return useQuery({
    queryKey: buildingKeys.devices(buildingId),
    queryFn: () => fetchBuildingDevices(buildingId),
    enabled: !!buildingId,
    staleTime: 2 * 60 * 1000, // 2 minuti
  });
};

/**
 * Hook per aggiungere un dispositivo a un edificio
 */
export const useAddDeviceToBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addDeviceToBuilding,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.devices(variables.buildingId) });
    },
  });
};

/**
 * Hook per rimuovere un dispositivo da un edificio
 */
export const useRemoveDeviceFromBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeDeviceFromBuilding,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.devices(variables.buildingId) });
    },
  });
};

/**
 * Hook per ottenere i membri di un edificio
 */
export const useBuildingMembers = (buildingId: number) => {
  return useQuery({
    queryKey: buildingKeys.members(buildingId),
    queryFn: () => fetchBuildingMembers(buildingId),
    enabled: !!buildingId,
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Hook per invitare un membro a un edificio
 */
export const useInviteMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: inviteMember,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.members(variables.buildingId) });
    },
  });
};

/**
 * Hook per aggiornare il ruolo di un membro
 */
export const useUpdateMemberRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateMemberRole,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.members(variables.buildingId) });
    },
  });
};

/**
 * Hook per rimuovere un membro da un edificio
 */
export const useRemoveMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeMember,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: buildingKeys.members(variables.buildingId) });
    },
  });
};

