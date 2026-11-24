
export interface Plan {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  duracion_dias: number;
  activo: boolean;
}

export interface PlanCrear {
  nombre: string;
  descripcion: string | null;
  precio: number;
  duracion_dias: number;
  activo: boolean;
}

export interface PlanActualizar {
  nombre?: string;
  descripcion?: string | null;
  precio?: number;
  duracion_dias?: number;
  activo?: boolean;
}

export interface PlanesPagina {
  items: Plan[];
  total: number;
  offset: number;
  limit: number;
}

export interface Suscripcion {
  id: number;
  cliente_id: number;
  plan_id: number;
  celda_id: number;
  fecha_inicio: string;
  fecha_fin: string;
  estado: 'ACTIVA' | 'VENCIDA' | 'CANCELADA';
}

export interface Pago {
  id: number;
  suscripcion_id: number;
  valor: number;
  fecha_pago: string;
  metodo_pago: string;
  referencia: string | null;
}

export interface ContratacionPagoCrear {
  identificacion: string;
  plan_id: number;
  celda_id: number;
  valor: number;
  metodo_pago: string;
  referencia: string | null;
}

export interface RenovacionPagoCrear {
  plan_id: number;
  valor: number;
  metodo_pago: string;
  referencia: string | null;
}

export interface ContratacionPagoRespuesta {
  suscripcion: Suscripcion;
  pago: Pago;
}
