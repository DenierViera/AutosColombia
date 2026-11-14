
import { Component, ChangeDetectorRef, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize, timeout } from 'rxjs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  username = '';
  password = '';
  showPassword = false;
  loading = false;
  errorMessage = '';

  togglePasswordVisibility(event: MouseEvent): void {
    event.preventDefault();
    event.stopPropagation();

    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    if (this.loading) return;

    if (!this.username.trim() || !this.password) {
      this.errorMessage = 'Ingresa tu usuario y contraseña.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService
      .login(this.username.trim(), this.password)
      .pipe(
        timeout(15000),
        finalize(() => {
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (response) => {
          if (!response.access_token || !response.usuario) {
            this.errorMessage =
              'El servidor devolvió una respuesta inválida.';
            this.cdr.detectChanges();
            return;
          }

          const rol = response.usuario.rol;

          if (rol === 'ADMINISTRADOR') {
            this.router.navigate(['/gestion/operadores']);
          } else if (rol === 'OPERADOR') {
            this.router.navigate(['/control-acceso']);
          } else {
            this.errorMessage = 'El usuario no tiene un rol válido.';
            this.cdr.detectChanges();
          }
        },
        error: (error) => {
          if (error.name === 'TimeoutError') {
            this.errorMessage =
              'El servidor tardó demasiado en responder.';
          } else if (error.status === 0) {
            this.errorMessage = 'No se pudo conectar con el servidor.';
          } else if (error.status === 401) {
            this.errorMessage =
              'Nombre de usuario o contraseña incorrectos.';
          } else {
            this.errorMessage =
              error.error?.detail || 'No fue posible iniciar sesión.';
          }

          this.cdr.detectChanges();
        },
      });
  }
}
