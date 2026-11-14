
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService, RolUsuario } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  return true;
};

export const roleGuard = (rol: RolUsuario): CanActivateFn => {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.isAuthenticated()) {
      return router.createUrlTree(['/login']);
    }

    if (!auth.hasRole(rol)) {
      return router.createUrlTree([
        auth.getRol() === 'OPERADOR'
          ? '/control-acceso'
          : '/gestion/operadores'
      ]);
    }

    return true;
  };
};
