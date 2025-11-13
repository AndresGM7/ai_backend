"""Generate modern visual reports for product pricing strategy analysis."""
from pathlib import Path
from typing import Optional
import pandas as pd


def generate_pricing_report(df: pd.DataFrame, uploads_dir: Path, cat_col: Optional[str] = None) -> None:
    """Generate comprehensive visual pricing strategy report.

    Creates multiple charts:
    1. Scatter plot: Elasticity vs Volume (product roles matrix)
    2. Bar chart: Product count by role
    3. Box plots: Distribution of elasticity and volume by role
    4. Heatmap: Strategy matrix
    5. Price recommendation distribution
    """
    try:
        # Configure matplotlib to use non-interactive backend BEFORE importing pyplot
        import matplotlib
        matplotlib.use('Agg')  # Use non-GUI backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np

        # Prepare data
        plot_df = df.copy()

        def to_num(v):
            try:
                return float(v)
            except Exception:
                return None

        plot_df['elasticidad_rel_num'] = plot_df['elasticidad_relativa'].apply(to_num)
        plot_df['volumen_rel_num'] = plot_df['volumen_relativo'].apply(to_num)
        plot_df = plot_df.dropna(subset=['elasticidad_rel_num', 'volumen_rel_num'])

        if plot_df.empty:
            print("Warning: No valid data for plotting (all elasticity/volume values are N/A)")
            return

        # Set modern style
        sns.set_theme(style='whitegrid', palette='husl')

        # 1. Main scatter plot: Elasticity vs Volume with roles
        fig, ax = plt.subplots(figsize=(12, 8))
        hue_col = cat_col if (cat_col and cat_col in plot_df.columns) else None

        # Create scatter plot
        scatter = sns.scatterplot(
            data=plot_df,
            x='volumen_rel_num',
            y='elasticidad_rel_num',
            hue=hue_col,
            style='rol_producto',
            palette='tab10',
            s=120,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.5,
            ax=ax
        )

        # Add reference lines
        ax.axvline(x=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.6, label='Volumen medio')
        ax.axhline(y=1.0, color='blue', linestyle='--', linewidth=1.5, alpha=0.6, label='Elasticidad unitaria')

        # Add quadrant labels
        try:
            x_range = plot_df['volumen_rel_num'].max() - plot_df['volumen_rel_num'].min()
            y_range = plot_df['elasticidad_rel_num'].max() - plot_df['elasticidad_rel_num'].min()

            x_mid_low = plot_df['volumen_rel_num'].quantile(0.25)
            x_mid_high = plot_df['volumen_rel_num'].quantile(0.75)
            y_mid_low = plot_df['elasticidad_rel_num'].quantile(0.25)
            y_mid_high = plot_df['elasticidad_rel_num'].quantile(0.75)

            ax.text(x_mid_low, y_mid_high, 'Promesa de valor\n(Elástico, Bajo vol)',
                    ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
            ax.text(x_mid_high, y_mid_high, 'Generador de tráfico\n(Elástico, Alto vol)',
                    ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
            ax.text(x_mid_low, y_mid_low, 'Estabilizador de ingresos\n(Inelástico, Bajo vol)',
                    ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
            ax.text(x_mid_high, y_mid_low, 'Generador de ganancias\n(Inelástico, Alto vol)',
                    ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
        except Exception:
            pass  # Skip labels if positioning fails

        ax.set_xlabel('Volumen Relativo (producto / promedio categoría)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Elasticidad Relativa |producto / categoría|', fontsize=12, fontweight='bold')
        ax.set_title('Matriz de Roles Estratégicos de Producto\nElasticidad vs Volumen',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = uploads_dir / 'roles_plot.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generado: {plot_path.name}")

        # 2. Bar chart: Product count by role
        fig, ax = plt.subplots(figsize=(10, 6))
        counts = plot_df['rol_producto'].value_counts().reset_index()
        counts.columns = ['Rol', 'Cantidad']

        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#95a5a6']
        bars = ax.bar(counts['Rol'], counts['Cantidad'], color=colors[:len(counts)],
                      edgecolor='black', linewidth=1.2, alpha=0.8)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)

        ax.set_xlabel('Rol Estratégico', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Productos', fontsize=12, fontweight='bold')
        ax.set_title('Distribución de Productos por Rol Estratégico',
                     fontsize=14, fontweight='bold', pad=20)
        ax.tick_params(axis='x', rotation=45)
        plt.xticks(ha='right')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        bar_path = uploads_dir / 'roles_counts.png'
        plt.savefig(bar_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generado: {bar_path.name}")

        # 3. Price recommendation distribution
        if 'recomendacion_precio' in plot_df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            rec_counts = plot_df['recomendacion_precio'].value_counts().reset_index()
            rec_counts.columns = ['Recomendación', 'Cantidad']

            # Order by severity
            order = ['Bajar mucho', 'Bajar', 'Mantener', 'Subir', 'Subir mucho']
            rec_counts['Recomendación'] = pd.Categorical(rec_counts['Recomendación'],
                                                         categories=order, ordered=True)
            rec_counts = rec_counts.sort_values('Recomendación')

            colors_rec = ['#c0392b', '#e67e22', '#f1c40f', '#27ae60', '#16a085']
            bars = ax.barh(rec_counts['Recomendación'], rec_counts['Cantidad'],
                          color=colors_rec[:len(rec_counts)], edgecolor='black',
                          linewidth=1.2, alpha=0.8)

            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', fontweight='bold', fontsize=11)

            ax.set_xlabel('Número de Productos', fontsize=12, fontweight='bold')
            ax.set_ylabel('Recomendación de Precio', fontsize=12, fontweight='bold')
            ax.set_title('Distribución de Recomendaciones de Precio',
                        fontsize=14, fontweight='bold', pad=20)
            ax.grid(axis='x', alpha=0.3)

            plt.tight_layout()
            rec_path = uploads_dir / 'price_recommendations.png'
            plt.savefig(rec_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Generado: {rec_path.name}")

        # 4. Box plots: Elasticity and Volume distribution by role
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Elasticity distribution
        plot_df['elasticidad_abs'] = plot_df['elasticidad_rel_num'].abs()
        sns.boxplot(data=plot_df, y='rol_producto', x='elasticidad_abs',
                   palette='Set2', ax=axes[0])
        axes[0].set_xlabel('Elasticidad Absoluta', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Rol de Producto', fontsize=11, fontweight='bold')
        axes[0].set_title('Distribución de Elasticidad por Rol', fontsize=12, fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)

        # Volume distribution
        sns.boxplot(data=plot_df, y='rol_producto', x='volumen_rel_num',
                   palette='Set3', ax=axes[1])
        axes[1].set_xlabel('Volumen Relativo', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('', fontsize=11)
        axes[1].set_title('Distribución de Volumen por Rol', fontsize=12, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        box_path = uploads_dir / 'distribution_by_role.png'
        plt.savefig(box_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generado: {box_path.name}")

        # 5. Summary statistics table
        agg_df = plot_df.copy()
        agg_df['elasticidad_rel_num_abs'] = agg_df['elasticidad_rel_num'].abs()

        # Group by category and role if category available
        group_cols = []
        if hue_col:
            group_cols = [hue_col, 'rol_producto']
        else:
            group_cols = ['rol_producto']

        stats = agg_df.groupby(group_cols).agg(
            productos=('rol_producto', 'count'),
            elasticidad_relativa_mean=('elasticidad_rel_num', 'mean'),
            elasticidad_relativa_std=('elasticidad_rel_num', 'std'),
            elasticidad_absoluta_mean=('elasticidad_rel_num_abs', 'mean'),
            volumen_relativo_mean=('volumen_rel_num', 'mean'),
            volumen_relativo_std=('volumen_rel_num', 'std')
        ).reset_index()

        stats_path = uploads_dir / 'summary_stats.csv'
        stats.to_csv(stats_path, index=False, sep=';', decimal=',')
        print(f"✓ Generado: {stats_path.name}")

        # 6. Overall statistics summary
        overall_stats = pd.DataFrame({
            'Métrica': [
                'Total Productos Analizados',
                'Elasticidad Media (abs)',
                'Volumen Relativo Medio',
                'Productos Elásticos (|e| >= 1)',
                'Productos Inelásticos (|e| < 1)',
                'Productos Alto Volumen (v > 1)',
                'Productos Bajo Volumen (v <= 1)'
            ],
            'Valor': [
                len(plot_df),
                f"{plot_df['elasticidad_abs'].mean():.2f}",
                f"{plot_df['volumen_rel_num'].mean():.2f}",
                len(plot_df[plot_df['elasticidad_abs'] >= 1]),
                len(plot_df[plot_df['elasticidad_abs'] < 1]),
                len(plot_df[plot_df['volumen_rel_num'] > 1]),
                len(plot_df[plot_df['volumen_rel_num'] <= 1])
            ]
        })

        overall_path = uploads_dir / 'overall_summary.csv'
        overall_stats.to_csv(overall_path, index=False, sep=';')
        print(f"✓ Generado: {overall_path.name}")

        print(f"\n✅ Reporte completo generado con {len(plot_df)} productos válidos")

    except Exception as e:
        # Plotting is optional; failure should not break the process
        print(f"⚠ Warning: Could not generate all charts: {e}")
        import traceback
        traceback.print_exc()
