
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export type RolUsuario = 'ADMINISTRADOR' | 'OPERADOR';

export interface UsuarioSesion {
  id: number;
  username: string;
  rol: RolUsuario;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: UsuarioSesion;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = '/auth';

  login(username: string, password: string): Observable<LoginResponse> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('usuario', JSON.stringify(response.usuario));
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('usuario');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getUsuario(): UsuarioSesion | null {
    const storedUser = localStorage.getItem('usuario');

    if (!storedUser) return null;

    try {
      return JSON.parse(storedUser) as UsuarioSesion;
    } catch {
      this.logout();
      return null;
    }
  }

  getRol(): RolUsuario | null {
    return this.getUsuario()?.rol ?? null;
  }

  hasRole(rol: RolUsuario): boolean {
    return this.getRol() === rol;
  }

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getUsuario();
  }
}
