/**
 * useSelectedBuilding Hook
 * 
 * Hook per gestire l'edificio attualmente selezionato dall'utente
 * Persiste la selezione in localStorage
 */

import { useState, useEffect } from 'react';
import { useBuildings } from './useBuildings';
import type { Building } from '../types/building';

const STORAGE_KEY = 'selectedBuildingId';

export const useSelectedBuilding = () => {
  const { data: buildings, isLoading, error } = useBuildings();
  
  const [selectedBuildingId, setSelectedBuildingId] = useState<number | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? parseInt(saved, 10) : null;
  });

  // Auto-seleziona primo edificio se non c'è selezione
  useEffect(() => {
    if (buildings && buildings.length > 0 && !selectedBuildingId) {
      const firstBuildingId = buildings[0].id;
      setSelectedBuildingId(firstBuildingId);
      localStorage.setItem(STORAGE_KEY, firstBuildingId.toString());
    }
  }, [buildings, selectedBuildingId]);

  // Verifica che l'edificio selezionato esista ancora
  useEffect(() => {
    if (buildings && selectedBuildingId) {
      const exists = buildings.some(b => b.id === selectedBuildingId);
      if (!exists && buildings.length > 0) {
        // Edificio non più disponibile, seleziona il primo
        const firstBuildingId = buildings[0].id;
        setSelectedBuildingId(firstBuildingId);
        localStorage.setItem(STORAGE_KEY, firstBuildingId.toString());
      }
    }
  }, [buildings, selectedBuildingId]);

  // Trova edificio selezionato
  const selectedBuilding: Building | undefined = buildings?.find(
    b => b.id === selectedBuildingId
  );

  // Handler per cambiare edificio
  const selectBuilding = (buildingId: number) => {
    setSelectedBuildingId(buildingId);
    localStorage.setItem(STORAGE_KEY, buildingId.toString());
  };

  // Clear selezione
  const clearSelection = () => {
    setSelectedBuildingId(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  return {
    buildings: buildings || [],
    selectedBuilding,
    selectedBuildingId,
    selectBuilding,
    clearSelection,
    isLoading,
    error,
    hasBuildings: (buildings?.length || 0) > 0,
  };
};

