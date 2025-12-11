import { DataProvider } from "@refinedev/core";
import { axiosInstance } from "../utils/api";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const dataProvider: DataProvider = {
  getApiUrl: () => API_URL,
  
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const url = `${API_URL}/${resource}`;
    
    // Costruisci parametri query
    const params: any = {};
    
    if (pagination) {
      params.page = pagination.current;
      params.per_page = pagination.pageSize;
    }
    
    if (filters && filters.length > 0) {
      filters.forEach((filter) => {
        if (filter.operator === "eq") {
          params[filter.field] = filter.value;
        } else if (filter.operator === "contains") {
          params[`${filter.field}_like`] = filter.value;
        }
      });
    }
    
    if (sorters && sorters.length > 0) {
      const sort = sorters[0];
      params.sort_by = sort.field;
      params.sort_order = sort.order;
    }

    try {
      const { data } = await axiosInstance.get(url, { params });
      
      return {
        data: data.items || data.data || data,
        total: data.total || data.count || (Array.isArray(data) ? data.length : 1),
        totalPages: data.pages || Math.ceil((data.total || 0) / (pagination?.pageSize || 10)),
      };
    } catch (error) {
      console.error(`Errore nel recupero di ${resource}:`, error);
      throw error;
    }
  },
  
  getOne: async ({ resource, id, meta }) => {
    const url = `${API_URL}/${resource}/${id}`;
    
    try {
      const { data } = await axiosInstance.get(url);
      return { data };
    } catch (error) {
      console.error(`Errore nel recupero di ${resource} con id ${id}:`, error);
      throw error;
    }
  },
  
  create: async ({ resource, variables, meta }) => {
    const url = `${API_URL}/${resource}`;
    
    try {
      const { data } = await axiosInstance.post(url, variables);
      return { data };
    } catch (error) {
      console.error(`Errore nella creazione di ${resource}:`, error);
      throw error;
    }
  },
  
  update: async ({ resource, id, variables, meta }) => {
    const url = `${API_URL}/${resource}/${id}`;
    
    try {
      const { data } = await axiosInstance.put(url, variables);
      return { data };
    } catch (error) {
      console.error(`Errore nell'aggiornamento di ${resource} con id ${id}:`, error);
      throw error;
    }
  },
  
  deleteOne: async ({ resource, id, meta }) => {
    const url = `${API_URL}/${resource}/${id}`;
    
    try {
      const { data } = await axiosInstance.delete(url);
      return { data };
    } catch (error) {
      console.error(`Errore nell'eliminazione di ${resource} con id ${id}:`, error);
      throw error;
    }
  },
  
  getMany: async ({ resource, ids, meta }) => {
    const responses = await Promise.all(
      ids.map(id => 
        axiosInstance.get(`${API_URL}/${resource}/${id}`)
      )
    );
    
    return {
      data: responses.map(response => response.data)
    };
  },
  
  // Metodi custom per dati solar
  custom: async ({ url, method, payload, query, headers }) => {
    try {
      const response = await axiosInstance({
        url: `${API_URL}${url}`,
        method: method || 'GET',
        data: payload,
        params: query,
        headers,
      });
      
      return { data: response.data };
    } catch (error) {
      console.error(`Errore nella chiamata custom ${method} ${url}:`, error);
      throw error;
    }
  },
  
  // Metodi specifici per il solar dashboard - Temporarily commented
  // getRealTimeData: async (deviceIds?: string[]) => {
  //   const params = deviceIds ? { device_ids: deviceIds.join(',') } : {};
  //   const { data } = await axiosInstance.get(`${API_URL}/devices/realtime`, { params });
  //   return { data };
  // },
  
  // getHistoricalData: async (deviceId: string, startDate: string, endDate: string) => {
  //   const { data } = await axiosInstance.get(`${API_URL}/devices/${deviceId}/history`, {
  //     params: { start_date: startDate, end_date: endDate }
  //   });
  //   return { data };
  // },
  
  // getDeviceAlarms: async (deviceId?: string) => {
  //   const url = deviceId 
  //     ? `${API_URL}/devices/${deviceId}/alarms`
  //     : `${API_URL}/alarms`;
  //   const { data } = await axiosInstance.get(url);
  //   return { data };
  // },
}; 