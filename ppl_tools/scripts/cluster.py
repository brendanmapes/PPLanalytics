import os
import textwrap

from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd

from plotly import graph_objects as go

from sentence_transformers import SentenceTransformer

from sklearn.manifold import TSNE
from sklearn.mixture import BayesianGaussianMixture, GaussianMixture

VERBOSITY = 10
VERBOSE_INTERVAL = 1

MODEL_OPTIONS = [
    'thenlper/gte-large',
    'all-MiniLM-L6-v2',
    'avsolatorio/GIST-Embedding-v0'
]

class CovarianceType(Enum):
    FULL = 'full'
    TIED = 'tied'
    DIAG = 'diag'
    SPHERICAL = 'spherical'

class ClusteringModelType(Enum):
    GMM = GaussianMixture
    DPGMM = BayesianGaussianMixture

@dataclass
class ClusteringConfig:
    n_clusters: int = 2
    max_iter: int = 1000

    model_type: ClusteringModelType = ClusteringModelType.GMM
    covariance_type: CovarianceType = CovarianceType.FULL
    weight_concentration_prior: float | None = 0.01


def get_args():
    p = ArgumentParser(description="Cluster 'What We Heard' R3 research findings computationally.")
    
    p.add_argument('data_file')
    p.add_argument('--model', default=MODEL_OPTIONS[0], type=str, choices=MODEL_OPTIONS)

    p.add_argument('--num_clusters', required=False, type=int, default=ClusteringConfig.n_clusters)

    return p.parse_args()


def load_data(path: str) -> pd.DataFrame:
    ext = Path(path).suffix
    if ext != '.csv':
        raise ValueError(
            'File must be saved as a .csv! '
            f'Instead, encountered: {ext}. '
            'Please redownload from airtable and try again.'
            )

    df = pd.read_csv(path)
    return df

# make embeddings
def embed(text: list[str], model_name: str) -> np.ndarray:
    model = SentenceTransformer(model_name)
    # setting tokenizer parallel environment variable to false,
    # to avoid getting a warning printed. see this link for more:
    # https://stackoverflow.com/questions/62691279/how-to-disable-tokenizers-parallelism-true-false-warning
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    embeddings = np.array(model.encode(text))
    return embeddings


def pairwise_euclidean_distances(data, means):
    # Compute the squared differences between each pair of vectors
    diff = data[:, np.newaxis, :] - means[np.newaxis, :, :]
    # Compute the Euclidean distances
    distances = np.sqrt(np.sum(diff**2, axis=-1))
    return distances



def cluster(embeddings: np.ndarray, config: ClusteringConfig) -> tuple[
        np.ndarray, np.ndarray, np.ndarray]:
    if config.model_type == ClusteringModelType.GMM:
        model = GaussianMixture(
            n_components=config.n_clusters,
            max_iter=config.max_iter,
            covariance_type=config.covariance_type.value,
            verbose=VERBOSITY,
            verbose_interval=VERBOSE_INTERVAL
        )
    elif config.model_type == ClusteringModelType.DPGMM:
        model = BayesianGaussianMixture(
            n_components=config.n_clusters,
            max_iter=config.max_iter,
            covariance_type=config.covariance_type.value,
            weight_concentration_prior=config.weight_concentration_prior,
            verbose=VERBOSITY,
            verbose_interval=VERBOSE_INTERVAL,
        )
    else:
        raise ValueError(f"Unsupported model type: {config.model_type}")

    labels = model.fit_predict(embeddings)
    probs = model.predict_proba(embeddings)

    # get distances between each embedding and each cluster mean
    pairwise_dists = pairwise_euclidean_distances(embeddings, model.means_)
    # dists to assigned cluster
    dists_to_assigned_cluster = pairwise_dists[np.arange(len(labels)), labels]

    # rename clusters in descending order by size for convenience

    # calculate cluster sizes
    _, cluster_sizes = np.unique(labels, return_counts=True)

    # get the new order of the clusters
    sorted_clusters = np.argsort(cluster_sizes)[::-1]

    # rename labels
    mapping = {old: new for new, old in enumerate(sorted_clusters)}
    labels = np.array([mapping[label] for label in labels])

    # reorder probs
    probs = probs[:, sorted_clusters]

    return probs, dists_to_assigned_cluster, labels


def make_plot(df, embeddings, labels, out_file=None):
    # create TSNE 2d embeddings ---
    tsne_embeddings = TSNE(n_components=2).fit_transform(embeddings)
    tsne_x = tsne_embeddings[:, 0]
    tsne_y = tsne_embeddings[:, 1]

    # create the plot ---
    text_preview = df['Key Data Points'].map(lambda x: '<br>'.join(textwrap.wrap(x, 75)) + '...')
    # remove NA from participant codes for display
    participant_code = np.where(
        df['Participant Code'].isna(),
        'Unknown',
        df['Participant Code']
        )

    fig = go.Figure()

    # check if multiproject
    project = np.zeros(len(df))
    multi_project = 'Project' in df.keys() and len(df['Project'].unique()) > 1
    hover_template = 'Cluster %{customdata[0]} - Participant %{customdata[2]}<br>%{customdata[1]}'
    if multi_project:
        project = df['Project'].to_numpy()
        hover_template += '<extra>%{customdata[3]}</extra>'
    else:
        hover_template += '<extra></extra>'


    for i in range(len(np.unique(labels))):
        cluster_idxs = (labels == i)

        custom_data = np.stack((
            labels[cluster_idxs],
            text_preview[cluster_idxs],
            participant_code[cluster_idxs],
            project[cluster_idxs],
            ), axis=-1)

        fig.add_trace(go.Scatter(
            x=tsne_x[cluster_idxs],
            y=tsne_y[cluster_idxs],
            mode='markers',
            marker_color=i,
            customdata=custom_data,
            hovertemplate=hover_template,
            name=i
        ))

    xrange = (tsne_x.min() - 1, tsne_x.max() + 1)
    yrange = (tsne_y.min() - 1, tsne_y.max() + 1)

    # Customize the plot
    fig.update_layout(
        xaxis_title='t-SNE Dimension 1',
        yaxis_title='t-SNE Dimension 2',
        legend_title='Cluster',
        template='plotly_white',
        showlegend=True,
        legend={
            'itemclick': 'toggleothers'
        },
        hovermode='closest',
        xaxis_range=xrange,
        yaxis_range=yrange,
    )
    if not out_file:
        out_file = Path.home() / "Downloads" / "cluster_visualization.html"
    fig.write_html(out_file)
    print(f'Saved interactive visualization to {out_file}')
    return


if __name__ == "__main__":
    args = get_args()

    df = load_data(args.data_file)
    # throw out rows with nan text
    df = df[~df['Key Data Points'].isna()]

    print('Creating embeddings...')
    embeddings = embed(df['Key Data Points'].tolist(), args.model)
    df['embeddings'] = embeddings.tolist()

    print('Clustering data points...')
    config = ClusteringConfig(n_clusters=args.num_clusters)
    probs, dists, assignments = cluster(embeddings, config)

    df['probs'] = probs.tolist()
    df['dists'] = dists.tolist()
    df['assignments'] = assignments

    print(args.data_file)
    df.to_csv(args.data_file, index=False)

    make_plot(df, embeddings, assignments)
