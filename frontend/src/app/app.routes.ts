
import { Routes } from '@angular/router';
import { authGuard, roleGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Iniciar sesión | Autos Colombia',
    loadComponent: () =>
      import('./auth/login/login').then(m => m.Login),
  },
  {
    path: 'control-acceso',
    title: 'Control de acceso | Autos Colombia',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./control-acceso/control-acceso').then(m => m.ControlAcceso),
  },
  {
    path: 'gestion/operadores',
    title: 'Operadores | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./operadores/operadores').then(m => m.Operadores),
  },
  {
    path: 'gestion/celdas',
    title: 'Celdas | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./celdas/celdas').then(m => m.Celdas),
  },
  {
    path: 'gestion/clientes',
    title: 'Clientes | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./clientes/clientes').then(m => m.Clientes),
  },
  {
    path: 'gestion/pagos',
    title: 'Pagos | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./pagos/pagos').then(m => m.Pagos),
  },
  {
    path: '',
    title: 'Inicio | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./home/home').then(m => m.Home),
  },
  {
    path: 'gestion/vehiculos',
    title: 'Vehículos | Autos Colombia',
    canActivate: [roleGuard('ADMINISTRADOR')],
    loadComponent: () =>
      import('./vehiculos/vehiculos').then(m => m.Vehiculos),
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login',
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
