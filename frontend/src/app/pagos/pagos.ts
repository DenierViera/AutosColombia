import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';


import { ApiService } from '../services/api.service';
import {
  Plan,
  PlanCrear,
  Suscripcion,
  RenovacionPagoCrear,
  Pago,
} from '../models/pago';
import { Cliente } from '../models/cliente';
import { Celda } from '../models/celda';

@Component({
  selector: 'app-pagos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pagos.html',
  styleUrl: './pagos.css',
})
export class Pagos implements OnInit {

  private readonly api = inject(ApiService);
  private readonly cdr = inject(ChangeDetectorRef);

  vista: 'planes' | 'contrataciones' | 'suscripciones' | 'historial' = 'planes';

  // PLANES
  planes: Plan[] = [];
  cargandoPlanes = false;
  guardandoPlan = false;
  mostrarFormularioPlan = false;

  nuevoPlan: PlanCrear = {
    nombre: '',
    descripcion: '',
    precio: 0,
    duracion_dias: 30,
    activo: true,
  };

  // CONTRATACIONES
  identificacion = '';
  propietario: Cliente | null = null;

  planesDisponibles: Plan[] = [];
  celdasDisponibles: Celda[] = [];

  planSeleccionado: number | null = null;
  celdaSeleccionada: number | null = null;

  metodoPago = 'EFECTIVO';
  referenciaPago = '';

  buscandoPropietario = false;
  guardandoContratacion = false;

    // SUSCRIPCIONES
  identificacionSuscripcion = '';
  suscripciones: Suscripcion[] = [];
  buscandoSuscripciones = false;

  suscripcionRenovar: number | null = null;
  planRenovacion: number | null = null;
  metodoPagoRenovacion = 'EFECTIVO';
  referenciaRenovacion = '';

  guardandoRenovacion = false;

  // HISTORIAL DE PAGOS
  pagos: Pago[] = [];
  cargandoPagos = false;

  // MENSAJES
  error = '';
  mensaje = '';

  ngOnInit(): void {
    this.cargarPlanes();
    this.cargarDatosContratacion();
    this.cargarPagos();
  }

  // GESTIÓN DE PLANES

  cargarPlanes(): void {
    this.cargandoPlanes = true;
    this.error = '';

    this.api.listPlans().subscribe({
      next: (respuesta) => {
        console.log('Respuesta de planes:', respuesta);

        this.planes = respuesta.items ?? [];
        this.planesDisponibles = this.planes.filter(
          plan => plan.activo
        );

        this.cargandoPlanes = false;
        this.cdr.detectChanges();

        console.log('Planes cargados:', this.planes);
        console.log('Cargando planes:', this.cargandoPlanes);
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error al cargar planes:', error);
        this.error = error.error?.detail || 'No se pudieron cargar los planes.';
        this.cargandoPlanes = false;
        this.cdr.detectChanges();
      },
    });
  }

  abrirFormularioPlan(): void {
    this.nuevoPlan = {
      nombre: '',
      descripcion: '',
      precio: 0,
      duracion_dias: 30,
      activo: true,
    };

    this.mostrarFormularioPlan = true;
    this.error = '';
  }

  crearPlan(): void {
    if (
      !this.nuevoPlan.nombre.trim() ||
      this.nuevoPlan.precio <= 0 ||
      this.nuevoPlan.duracion_dias <= 0
    ) {
      this.error = 'Completa correctamente los datos del plan.';
      return;
    }

    this.guardandoPlan = true;
    this.error = '';

    this.api.createPlan({
      ...this.nuevoPlan,
      nombre: this.nuevoPlan.nombre.trim(),
      descripcion: this.nuevoPlan.descripcion?.trim() || null,
    }).subscribe({
      next: () => {
        this.guardandoPlan = false;
        this.mostrarFormularioPlan = false;
        this.mensaje = 'Plan creado correctamente.';
        this.cargarPlanes();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo crear el plan.';
        this.guardandoPlan = false;
      },
    });
  }

  desactivarPlan(plan: Plan): void {
    if (!confirm(`¿Deseas desactivar el plan "${plan.nombre}"?`)) {
      return;
    }

    this.error = '';

    this.api.deactivatePlan(plan.id).subscribe({
      next: () => {
        this.mensaje = 'Plan desactivado correctamente.';
        this.cargarPlanes();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo desactivar el plan.';
      },
    });
  }

  // CONTRATACIONES

  cargarDatosContratacion(): void {
    this.api.listAvailableCells().subscribe({
      next: (celdas) => {
        this.celdasDisponibles = celdas;
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudieron cargar las celdas.';
      },
    });
  }

  buscarPropietario(): void {
    const identificacion = this.identificacion.trim();

    if (!identificacion) {
      this.error = 'Ingresa la identificación del propietario.';
      return;
    }

    this.buscandoPropietario = true;
    this.propietario = null;
    this.error = '';
    this.mensaje = '';

    this.api.getClientByIdentification(identificacion).subscribe({
      next: (cliente) => {
        this.propietario = cliente;
        this.buscandoPropietario = false;
        this.cdr.detectChanges();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se encontró el propietario.';
        this.buscandoPropietario = false;
        this.cdr.detectChanges();
      },
    });
  }

  contratar(): void {
    if (!this.propietario) {
      this.error = 'Primero debes buscar un propietario registrado.';
      return;
    }

    if (!this.planSeleccionado || !this.celdaSeleccionada) {
      this.error = 'Selecciona un plan y una celda.';
      return;
    }

    const plan = this.planesDisponibles.find(
      item => item.id === this.planSeleccionado
    );

    if (!plan) {
      this.error = 'El plan seleccionado no está disponible.';
      return;
    }

    this.guardandoContratacion = true;
    this.error = '';
    this.mensaje = '';

    this.api.contractWithPayment({
      identificacion: this.propietario.identificacion,
      plan_id: plan.id,
      celda_id: this.celdaSeleccionada,
      valor: plan.precio,
      metodo_pago: this.metodoPago,
      referencia: this.referenciaPago.trim() || null,
    }).subscribe({
      next: () => {
        this.guardandoContratacion = false;
        this.mensaje = 'Contratación y pago registrados correctamente.';

        this.identificacion = '';
        this.propietario = null;
        this.planSeleccionado = null;
        this.celdaSeleccionada = null;
        this.metodoPago = 'EFECTIVO';
        this.referenciaPago = '';

        this.cargarDatosContratacion();
        this.cargarPagos();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo registrar la contratación.';
        this.guardandoContratacion = false;
      },
    });
  }

  // CONSULTAR SUSCRIPCIONES

  buscarSuscripciones(): void {
    const identificacion = this.identificacionSuscripcion.trim();

    if (!identificacion) {
      this.error = 'Ingresa la identificación del propietario.';
      return;
    }

    this.buscandoSuscripciones = true;
    this.error = '';
    this.suscripciones = [];

    this.api.getClientByIdentification(identificacion).subscribe({
      next: (cliente) => {
        this.api.listClientSubscriptions(cliente.id).subscribe({
          next: (suscripciones) => {
            this.suscripciones = suscripciones;
            this.buscandoSuscripciones = false;
            this.cdr.detectChanges();
          },
          error: (error: HttpErrorResponse) => {
            this.error = error.error?.detail || 'No se pudieron consultar las suscripciones.';
            this.buscandoSuscripciones = false;
            this.cdr.detectChanges();
          },
        });
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se encontró el propietario.';
        this.buscandoSuscripciones = false;
        this.cdr.detectChanges();
      },
    });
  }

  prepararRenovacion(suscripcion: Suscripcion): void {
    this.suscripcionRenovar = suscripcion.id;
    this.planRenovacion = suscripcion.plan_id;
    this.referenciaRenovacion = '';
    this.error = '';
  }

  renovarSuscripcion(): void {
    if (!this.suscripcionRenovar || !this.planRenovacion) {
      this.error = 'Selecciona un plan para renovar.';
      return;
    }

    const plan = this.planesDisponibles.find(
      item => item.id === this.planRenovacion
    );

    if (!plan) {
      this.error = 'El plan seleccionado no está disponible.';
      return;
    }

    const data: RenovacionPagoCrear = {
      plan_id: plan.id,
      valor: plan.precio,
      metodo_pago: this.metodoPagoRenovacion,
      referencia: this.referenciaRenovacion.trim() || null,
    };

    this.guardandoRenovacion = true;
    this.error = '';

    this.api.renewSubscription(this.suscripcionRenovar, data).subscribe({
      next: () => {
        this.guardandoRenovacion = false;
        this.suscripcionRenovar = null;
        this.metodoPagoRenovacion = 'EFECTIVO';
        this.referenciaRenovacion = '';
        this.mensaje = 'Suscripción renovada y pago registrado correctamente.';
        this.buscarSuscripciones();
        this.cargarPagos();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo renovar la suscripción.';
        this.guardandoRenovacion = false;
      },
    });
  }

  cancelarSuscripcion(suscripcion: Suscripcion): void {
    if (!confirm('¿Estás seguro de cancelar esta suscripción?')) {
      return;
    }

    this.error = '';

    this.api.cancelSubscription(suscripcion.id).subscribe({
      next: () => {
        this.mensaje = 'Suscripción cancelada correctamente.';
        this.buscarSuscripciones();
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo cancelar la suscripción.';
      },
    });
  }
  // HISTORIAL DE PAGOS

  cargarPagos(): void {
    this.cargandoPagos = true;
    this.error = '';

    this.api.listPayments().subscribe({
      next: (pagos) => {
        this.pagos = pagos;
        this.cargandoPagos = false;
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.detail || 'No se pudo cargar el historial de pagos.';
        this.cargandoPagos = false;
      },
    });
  }

  nombrePlan(planId: number): string {
    return this.planes.find(
      plan => plan.id === planId
    )?.nombre || `Plan #${planId}`;
  }
}