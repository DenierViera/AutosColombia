import { Vehiculo } from './vehiculo';

export interface ClienteCrear {
  identificacion: string;
  nombre_completo: string;
  telefono: string;
}

export type ClienteActualizar = Partial<ClienteCrear>;

export interface Cliente extends ClienteCrear {
  id: number;
}

export interface ClienteDetalle extends Cliente {
  vehiculos: Vehiculo[];
}

export interface ClientesPagina {
  items: Cliente[];
  total: number;
  offset: number;
  limit: number;
}