import { HttpClient } from '@angular/common/http';
import { inject, Injectable, InjectionToken } from '@angular/core';
import { timeout } from 'rxjs';
import {
  Vehiculo,
  VehiculoActualizar,
  VehiculoCrear,
  VehiculoConClienteCrear,
  VehiculosPagina,
} from '../models/vehiculo';
import {
  Cliente,
  ClienteActualizar,
  ClienteCrear,
  ClienteDetalle,
  ClientesPagina,
} from '../models/cliente';
import {
  Plan,
  PlanCrear,
  PlanActualizar,
  PlanesPagina,
  Pago,
  Suscripcion,
  ContratacionPagoCrear,
  RenovacionPagoCrear,
  ContratacionPagoRespuesta,
} from '../models/pago';
import {
  Celda,
} from '../models/celda';
// Mismo origen: el proxy de desarrollo define el destino real del backend.
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', { factory: () => '' });

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly vehicles = `${this.base}/vehiculos`;
  private readonly clients = `${this.base}/clientes`;
  private readonly plans = `${this.base}/planes`;
  private readonly payments = `${this.base}/pagos`;
  private readonly subscriptions = `${this.base}/suscripciones`;

  health() {
    return this.http.get<{ status?: unknown } | null>(`${this.base}/health`);
  }
  list(offset: number, limit: number) {
    return this.http
      .get<VehiculosPagina>(this.vehicles, { params: { offset, limit } })
      .pipe(timeout(15000));
  }
  get(id: number) {
    return this.http.get<Vehiculo>(`${this.vehicles}/${id}`).pipe(timeout(15000));
  }
  create(data: VehiculoCrear) {
    return this.http.post<Vehiculo>(this.vehicles, data).pipe(timeout(15000));
  }
  registrarVehiculoYEntrada(data: {
    vehiculo: VehiculoConClienteCrear;
    celda_id: number;
    operador_id: number;
  }) {
    return this.http
      .post<import('../models/estancia').Estancia>(
        `${this.base}/estancias/entrada/registrar-vehiculo`,
        data,
      )
      .pipe(timeout(15000));
  }
  update(id: number, data: VehiculoActualizar) {
    return this.http.patch<Vehiculo>(`${this.vehicles}/${id}`, data).pipe(timeout(15000));
  }
  delete(id: number) {
    return this.http.delete<void>(`${this.vehicles}/${id}`).pipe(timeout(15000));
  }
  listClients(offset: number, limit: number) {
    return this.http
      .get<ClientesPagina>(this.clients, { params: { offset, limit } })
      .pipe(timeout(15000));
  }

  getClient(id: number) {
    return this.http
      .get<ClienteDetalle>(`${this.clients}/${id}`)
      .pipe(timeout(15000));
  }

  getClientByIdentification(identificacion: string) {
    return this.http
      .get<Cliente>(
        `${this.clients}/identificacion/${encodeURIComponent(identificacion)}`
      )
      .pipe(timeout(15000));
  }

  createClient(data: ClienteCrear) {
    return this.http
      .post<Cliente>(this.clients, data)
      .pipe(timeout(15000));
  }

  updateClient(id: number, data: ClienteActualizar) {
    return this.http
      .patch<Cliente>(`${this.clients}/${id}`, data)
      .pipe(timeout(15000));
  }

  deleteClient(id: number) {
    return this.http
      .delete<void>(`${this.clients}/${id}`)
      .pipe(timeout(15000));
  }
  // CELDAS DISPONIBLES

  listAvailableCells() {
    return this.http
      .get<Celda[]>(`${this.base}/celdas/disponibles`)
      .pipe(timeout(15000));
  }
  // PLANES

  listPlans(offset = 0, limit = 100) {
    return this.http
      .get<PlanesPagina>(this.plans, { params: { offset, limit } })
      .pipe(timeout(15000));
  }

  createPlan(data: PlanCrear) {
    return this.http
      .post<Plan>(this.plans, data)
      .pipe(timeout(15000));
  }

  updatePlan(id: number, data: PlanActualizar) {
    return this.http
      .patch<Plan>(`${this.plans}/${id}`, data)
      .pipe(timeout(15000));
  }

  deactivatePlan(id: number) {
    return this.http
      .patch<Plan>(`${this.plans}/${id}/desactivar`, {})
      .pipe(timeout(15000));
  }

  // CONTRATACIONES Y PAGOS

  contractWithPayment(data: ContratacionPagoCrear) {
    return this.http
      .post<ContratacionPagoRespuesta>(
        `${this.payments}/contratar`,
        data,
      )
      .pipe(timeout(15000));
  }

  listPayments() {
    return this.http
      .get<Pago[]>(this.payments)
      .pipe(timeout(15000));
  }

  listSubscriptionPayments(id: number) {
    return this.http
      .get<Pago[]>(`${this.payments}/suscripcion/${id}`)
      .pipe(timeout(15000));
  }

  // SUSCRIPCIONES

  listClientSubscriptions(clienteId: number) {
    return this.http
      .get<Suscripcion[]>(
        `${this.subscriptions}/cliente/${clienteId}`,
      )
      .pipe(timeout(15000));
  }

  renewSubscription(id: number, data: RenovacionPagoCrear) {
    return this.http
      .post<ContratacionPagoRespuesta>(
        `${this.subscriptions}/${id}/renovar`,
        data,
      )
      .pipe(timeout(15000));
  }

  cancelSubscription(id: number) {
    return this.http
      .post<Suscripcion>(
        `${this.subscriptions}/${id}/cancelar`,
        {},
      )
      .pipe(timeout(15000));
  }
}

