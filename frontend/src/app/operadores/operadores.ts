
import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  FormBuilder,
  ReactiveFormsModule,
  ValidatorFn,
} from '@angular/forms';

import { OperadoresService } from '../services/operadores.service';
import {
  Operador,
  OperadorActualizar,
  OperadorCrear,
} from '../models/operador';
import { ErrorApi } from '../models/vehiculo';

const nonBlank: ValidatorFn = (control) =>
  typeof control.value === 'string' && control.value.trim()
    ? null
    : { required: true };

const passwordValidator: ValidatorFn = (control) => {
  const value = control.value;
  if (!value) return null;
  return typeof value === 'string' && value.length >= 8
    ? null
    : { minlength: true };
};

type Field = keyof OperadorCrear;

@Component({
  selector: 'app-operadores',
  imports: [ReactiveFormsModule],
  templateUrl: './operadores.html',
  styleUrl: './operadores.css',
})
export class Operadores {
  private readonly api = inject(OperadoresService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);

  readonly fields = [
    { key: 'nombre' as const, label: 'Nombre' },
    { key: 'telefono' as const, label: 'Teléfono' },
    { key: 'username' as const, label: 'Nombre de usuario' },
    { key: 'password' as const, label: 'Contraseña' },
  ];

  readonly form = this.fb.group({
    nombre: this.fb.nonNullable.control('', nonBlank),
    telefono: this.fb.nonNullable.control('', nonBlank),
    username: this.fb.nonNullable.control('', nonBlank),
    password: this.fb.nonNullable.control('', passwordValidator),
  });

  readonly items = signal<Operador[]>([]);
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly limit = 10;

  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly busy = computed(() => this.loading() || this.saving());

  readonly showForm = signal(false);
  readonly editing = signal<number | null>(null);
  readonly pendingDelete = signal<Operador | null>(null);

  readonly listError = signal('');
  readonly actionError = signal('');
  readonly success = signal('');

  readonly page = computed(
    () => Math.floor(this.offset() / this.limit) + 1,
  );

  readonly pages = computed(
    () => Math.max(1, Math.ceil(this.total() / this.limit)),
  );

  constructor() {
    this.load();
  }

  load(offset = this.offset()): void {
    if (this.busy()) return;

    this.loading.set(true);
    this.listError.set('');

    this.api.list(offset, this.limit)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.loading.set(false);

          if (offset > 0 && offset >= data.total) {
            this.load(
              Math.max(
                0,
                Math.floor((data.total - 1) / this.limit) * this.limit,
              ),
            );
            return;
          }

          this.items.set(data.items);
          this.total.set(data.total);
          this.offset.set(offset);
        },
        error: (error) => {
          this.loading.set(false);
          this.listError.set(this.errorMessage(error));
        },
      });
  }

  newOperator(): void {
    if (this.busy()) return;

    this.form.reset({
      nombre: '',
      telefono: '',
      username: '',
      password: '',
    });

    this.editing.set(null);
    this.showForm.set(true);
    this.pendingDelete.set(null);
    this.actionError.set('');
    this.success.set('');
  }

  edit(operator: Operador): void {
    if (this.busy()) return;

    this.loading.set(true);
    this.actionError.set('');
    this.success.set('');
    this.pendingDelete.set(null);

    this.api.get(operator.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.loading.set(false);
          this.editing.set(data.id);

          this.form.reset({
            nombre: data.nombre,
            telefono: data.telefono,
            username: data.username ?? '',
            password: '',
          });

          this.showForm.set(true);
        },
        error: (error) => {
          this.loading.set(false);
          this.actionError.set(this.errorMessage(error));
        },
      });
  }

  cancel(): void {
    if (this.busy()) return;

    this.showForm.set(false);
    this.pendingDelete.set(null);
    this.actionError.set('');
  }

  fieldError(field: Field): string {
    const control = this.form.controls[field];

    if (!control.touched || !control.errors) return '';

    if (control.errors['server']) {
      return String(control.errors['server']);
    }

    if (control.errors['required']) {
      return 'Este campo es obligatorio.';
    }

    if (control.errors['minlength']) {
      return 'La contraseña debe tener al menos 8 caracteres.';
    }

    return 'Revisa este campo.';
  }

  save(): void {
    if (this.busy()) return;

    this.form.markAllAsTouched();

    const isCreating = this.editing() === null;
    const value = this.form.getRawValue();

    if (isCreating && !value.password) {
      this.form.controls.password.setErrors({ required: true });
    }

    if (this.form.invalid) {
      this.actionError.set(
        'Revisa los campos señalados antes de guardar el operador.',
      );
      return;
    }

    const id = this.editing();

    const common = {
      nombre: value.nombre.trim(),
      telefono: value.telefono.trim(),
      username: value.username.trim(),
    };

    const request = id === null
      ? this.api.create({
          ...common,
          password: value.password,
        } satisfies OperadorCrear)
      : this.api.update(id, {
          ...common,
          ...(value.password ? { password: value.password } : {}),
        } satisfies OperadorActualizar);

    this.saving.set(true);
    this.actionError.set('');
    this.success.set('');

    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (operator) => {
        this.saving.set(false);
        this.showForm.set(false);

        this.success.set(
          `Operador ${operator.nombre} ${
            id === null ? 'registrado' : 'actualizado'
          } correctamente.`,
        );

        this.load();
      },
      error: (error: HttpErrorResponse) => {
        this.saving.set(false);
        this.actionError.set(this.errorMessage(error));

        const body = error.error as ErrorApi | null;

        if (error.status === 422 && Array.isArray(body?.detail)) {
          for (const issue of body.detail) {
            const field = issue.loc.at(-1);

            if (
              typeof field === 'string' &&
              Object.hasOwn(this.form.controls, field)
            ) {
              this.setFieldError(
                field as Field,
                'El servicio rechazó este valor. Revisa el campo.',
              );
            }
          }
        }
      },
    });
  }

  toggleAccess(operator: Operador): void {
    if (this.busy()) return;

    const newStatus = !operator.acceso_activo;

    this.saving.set(true);
    this.actionError.set('');
    this.success.set('');

    this.api.updateAccess(operator.id, { activo: newStatus })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.saving.set(false);

          this.items.update((items) =>
            items.map((item) =>
              item.id === updated.id ? updated : item,
            ),
          );

          this.success.set(
            `Acceso de ${updated.nombre}: ${
              updated.acceso_activo ? 'activado' : 'desactivado'
            }.`,
          );
        },
        error: (error) => {
          this.saving.set(false);
          this.actionError.set(this.errorMessage(error));
        },
      });
  }

  private setFieldError(field: Field, message: string): void {
    this.form.controls[field].setErrors({ server: message });
    this.form.controls[field].markAsTouched();
  }

  confirmDelete(operator: Operador): void {
    if (this.busy()) return;

    this.pendingDelete.set(operator);
    this.showForm.set(false);
    this.actionError.set('');
    this.success.set('');
  }

  remove(): void {
    const operator = this.pendingDelete();

    if (!operator || this.busy()) return;

    this.saving.set(true);
    this.actionError.set('');

    this.api.delete(operator.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.pendingDelete.set(null);
          this.success.set(
            `Operador ${operator.nombre} eliminado correctamente.`,
          );
          this.load();
        },
        error: (error) => {
          this.saving.set(false);
          this.actionError.set(this.errorMessage(error, true));

          if (error.status === 404) {
            this.pendingDelete.set(null);
            this.load();
          }
        },
      });
  }

  private errorMessage(
    error: HttpErrorResponse,
    deleting = false,
  ): string {
    if (error.status === 404) {
      return 'El operador o sus credenciales no existen.';
    }

    if (error.status === 409) {
      return deleting
        ? 'No se puede eliminar: existen registros relacionados.'
        : 'El nombre de usuario ya existe o hay un conflicto.';
    }

    if (error.status === 422) {
      return 'Revisa los datos: hay campos que no cumplen las validaciones.';
    }

    return 'No se pudo conectar con el servicio. Comprueba la conexión e inténtalo nuevamente.';
  }
}
