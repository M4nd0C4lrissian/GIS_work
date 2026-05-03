import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import math
import numpy as np

#Input
#   gdf : the polygons to plot
#   features : features to plot (expecting geometry such as LineStrings) - will test with other feature types
#   save_filepath : optional path where to save the graph, if not present, plot displayed and deleted
#   color_norm_value : optional string representing the gdf column values to normalize polygon coloring according to some condition of the CSDs (i.e. %rental properties)
#   label_names : whether or not you want the sub-divisions to be names. note that we will have to change the name from 'CDNAME' to something else when we get the true data.
# NOTE: the gdf we plot does not need to be the gdf we searched features over - this is helpful, as we could pass in much more granular CSDs, while querying over the larger Toronto CSD for the API call
def plot_features_over_geometry(gdf, features, feature_keys, save_filepath=None, color_norm_value=None, label_names=True):
            
    # looks like you need to make the fig and ax separately
    fig, ax = plt.subplots(figsize=(10, 10))
        
    #can normalize polygon coloring according to some characteristic of the csd population
    vmin=0
    vmax=100
    if color_norm_value:
        vmin = gdf[color_norm_value].min()
        vmax = gdf[color_norm_value].max()

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.Reds

    gdf.plot(
        ax=ax,
        cmap=cmap,
        linewidth=0.5,
        edgecolor='black',
        norm=norm
    )

    if label_names:

        for _, row in gdf.iterrows():
            centroid = row['geometry'].centroid
            ax.annotate(
                text=row['CDNAME'],
                xy=(centroid.x, centroid.y),
                ha='center',
                va='center',
                fontsize=8,
                color='black'
            )

    #need each feature to have its own color and legend should reflect that
    feature_gdf_list = []
    legend_handles = []
    #generate N distinct colors based on number of unique feature keys
    colors = plt.cm.tab10.colors
    color_map = {tup: colors[i % len(colors)] for i, tup in enumerate(feature_keys)}

    for tup in feature_keys:
        color = color_map[tup]

        # filter for only the high-level feature type
        temp_f = features.dropna(subset=[tup[0]])
        # then filter for low-level feature type
        temp_f = temp_f[temp_f[tup[0]] == tup[1]]

        # add one legend handle per feature_key (not per geometry type)
        legend_handles.append(mpatches.Patch(color=color, label=tup[1]))

        # then we further filter through unique geometries
        for g in temp_f.geometry.geom_type.unique():
            feature_gdf_list.append((temp_f[temp_f.geometry.geom_type == g], color))

    for feature_gdf, color in feature_gdf_list:
        feature_gdf.plot(ax=ax, color=color, linewidth=0.5)

    ax.legend(handles=legend_handles, loc='upper right')

    # features.plot(ax=ax, color='blue', linewidth=0.5)

    if save_filepath:
        plt.savefig(save_filepath)
    else:
        plt.show()
        
def plot_polygons(gdf, color_val, title, save_filepath=None):
    # Use a copy so we don't mutate the original
    color_val = color_val.copy().astype(float)

    # Mark missing/invalid values as NaN so cmap renders them as "bad" (grey)
    color_val[color_val < 0] = np.nan

    # Choose your colormap here — change to any plt.cm.* you like
    cmap = truncate_cmap(plt.cm.Reds, minval=0.0, maxval=0.8)
    cmap = cmap.with_extremes(bad='grey')  # NaN polygons → grey

    # # TODO: make norm an argument
    # norm = mcolors.Normalize(
    #     vmin=np.nanmin(color_val),
    #     vmax=np.nanmax(color_val)
    # )
    
    norm = mcolors.PowerNorm(gamma=2, vmin=np.nanmin(color_val), vmax=np.nanmax(color_val))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title, fontsize=16, pad=15)
    ax.set_xticks([])
    ax.set_yticks([])

    gdf.plot(
        ax=ax,
        column=color_val,   # pass values directly; geopandas handles NaN → bad color
        cmap=cmap,
        norm=norm,
        linewidth=0.5,
        # edgecolor='black',
        edgecolor='none',
        missing_kwds={"color": "grey"},  # belt-and-suspenders for truly missing rows
    )

    # Manually build a ScalarMappable for the colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
    # cbar.set_label(percent_metric, fontsize=12)

    # Format colorbar ticks as percentages
    cbar.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 100:.0f}%")
    )

    if save_filepath:
        plt.savefig(save_filepath, bbox_inches='tight')
    else:
        plt.show()
        

from matplotlib.colors import LinearSegmentedColormap
   
def truncate_cmap(cmap, minval=0.0, maxval=0.5):
    """Slice a colormap to only use the range [minval, maxval]."""
    return LinearSegmentedColormap.from_list(
        f"trunc({cmap.name},{minval:.2f},{maxval:.2f})",
        cmap(np.linspace(minval, maxval, 256))
    )