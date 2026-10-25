
export interface CeldaCrear {
  codigo: string;
  tipo: string;
}

export type CeldaActualizar = Partial<CeldaCrear>;

export interface Celda extends CeldaCrear {
  id: number;
}

export type EstadoCelda = 'Disponible' | 'Ocupada';

export interface CeldaConEstado extends Celda {
  estado: EstadoCelda;
}

export interface CeldasPagina {
  items: CeldaConEstado[];
  total: number;
  offset: number;
  limit: number;
  disponibles: number;
  ocupadas: number;
}
