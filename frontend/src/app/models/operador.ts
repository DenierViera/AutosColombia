
export interface OperadorCrear {
  nombre: string;
  telefono: string;
  username: string;
  password: string;
}

export interface OperadorActualizar {
  nombre?: string;
  telefono?: string;
  username?: string;
  password?: string;
}

export interface Operador {
  id: number;
  nombre: string;
  telefono: string;
  username: string | null;
  acceso_activo: boolean;
}

export interface OperadoresPagina {
  items: Operador[];
  total: number;
  offset: number;
  limit: number;
}

export interface AccesoActualizar {
  activo: boolean;
}
