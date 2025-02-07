from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QComboBox, QSpinBox, QProgressBar, QLabel,
                               QGroupBox, QFormLayout, QDoubleSpinBox,
                               QCheckBox, QStackedWidget, QSizePolicy)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt

class ClusterTabUI:
    def setup_ui(self, widget):
        self.main_layout = QVBoxLayout(widget)

        self.setup_top_bar()
        self.setup_content_area()

        self.main_layout.addLayout(self.top_bar)
        self.main_layout.addLayout(self.content_layout)

    def setup_top_bar(self):
        self.top_bar = QHBoxLayout()

        # Explanatory text
        self.explanation = QLabel(
            "This tool clusters similar text entries using natural language processing. "
            "Select a CSV file, choose the text column to analyze, set clustering options, and run the analysis."
        )
        self.explanation.setWordWrap(True)
        # self.explanation.setFixedWidth(400)
        self.top_bar.addWidget(self.explanation, 3)

        # File and column selection
        file_column_layout = QFormLayout()
        file_column_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.file_label)

        self.file_btn = QPushButton("Select CSV File")
        file_layout.addWidget(self.file_btn)
        file_column_layout.addRow(file_layout)

        self.column_combo = QComboBox()
        self.column_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.column_combo.setEnabled(False)
        file_column_layout.addRow("Select Text Column:", self.column_combo)

        self.top_bar.addLayout(file_column_layout, 2)

    def setup_content_area(self):
        self.content_layout = QHBoxLayout()

        self.setup_left_pane()
        self.setup_right_pane()

        self.content_layout.addWidget(self.left_pane, 1)
        self.content_layout.addWidget(self.right_pane, 2)


    def setup_left_pane(self):
        self.left_pane = QWidget()
        left_layout = QVBoxLayout(self.left_pane)

        self.setup_model_options()
        self.setup_run_control()

        left_layout.addWidget(self.model_options_group)
        left_layout.addLayout(self.run_control_layout)
        left_layout.addStretch()

    def setup_right_pane(self):
        self.right_pane = QWidget()
        right_layout = QVBoxLayout(self.right_pane)


        self.setup_results_area()
        self.setup_export_area()

        right_layout.addWidget(self.results_group, 1)
        right_layout.addWidget(self.export_group)

    def setup_model_options(self):
        self.model_options_group = QGroupBox("Model Options")
        model_options_layout = QVBoxLayout()

        # Number of clusters
        clusters_layout = QHBoxLayout()
        clusters_layout.addWidget(QLabel("Number of Clusters:"))
        self.cluster_spin = QSpinBox()
        self.cluster_spin.setRange(2, 100)
        self.cluster_spin.setValue(10)
        clusters_layout.addWidget(self.cluster_spin)
        model_options_layout.addLayout(clusters_layout)

        # Advanced options
        self.advanced_checkbox = QCheckBox("Show Advanced Options")
        model_options_layout.addWidget(self.advanced_checkbox)

        self.advanced_group = QGroupBox()
        self.advanced_group.setVisible(False)
        advanced_layout = QVBoxLayout()
        # advanced_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        # Embedding Model
        advanced_layout.addWidget(QLabel("Embedding Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(['thenlper/gte-large', 'all-MiniLM-L6-v2', 'avsolatorio/GIST-Embedding-v0'])
        advanced_layout.addWidget(self.model_combo)

        # Clustering Model
        advanced_layout.addWidget(QLabel("Clustering Model:"))
        self.cluster_model_combo = QComboBox()
        self.cluster_model_combo.addItems(['Gaussian Mixture', 'Bayesian Gaussian Mixture'])
        advanced_layout.addWidget(self.cluster_model_combo)

        # Model-specific options
        self.model_options_stack = QStackedWidget()

        # Gaussian Mixture options
        gm_widget = QWidget()
        gm_layout = QFormLayout()
        gm_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        # gm_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        gm_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.gm_covariance_type = QComboBox()
        self.gm_covariance_type.addItems(['full', 'tied', 'diag', 'spherical'])

        gm_layout.addRow("Covariance Type:", self.gm_covariance_type)
        gm_widget.setLayout(gm_layout)
        self.model_options_stack.addWidget(gm_widget)

        # Bayesian Gaussian Mixture options
        bgm_widget = QWidget()
        bgm_layout = QFormLayout()

        self.bgm_weight_concentration_prior = QDoubleSpinBox()
        self.bgm_weight_concentration_prior.setRange(0, 1)
        self.bgm_weight_concentration_prior.setDecimals(4)
        self.bgm_weight_concentration_prior.setValue(0.0001)
        self.bgm_weight_concentration_prior.setSingleStep(0.0001)
        # bgm_layout.addWidget(self.bgm_weight_concentration_prior)
        bgm_layout.addRow("Prior Concentration:", self.bgm_weight_concentration_prior)
        self.bgm_covariance_type = QComboBox()
        self.bgm_covariance_type.addItems(['full', 'tied', 'diag', 'spherical'])
        # bgm_layout.addWidget(self.bgm_covariance_type)
        bgm_layout.addRow("Covariance Type:", self.bgm_covariance_type)
        # bgm_layout.addStretch()
        bgm_widget.setLayout(bgm_layout)
        self.model_options_stack.addWidget(bgm_widget)

        advanced_layout.addWidget(self.model_options_stack)

        # Max Iterations
        advanced_layout.addWidget(QLabel("Max Iterations:"))
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(10, 500)
        self.max_iter_spin.setValue(100)
        advanced_layout.addWidget(self.max_iter_spin)

        advanced_layout.addStretch()

        self.advanced_group.setLayout(advanced_layout)
        model_options_layout.addWidget(self.advanced_group)

        self.model_options_group.setLayout(model_options_layout)

    def setup_run_control(self):
        self.run_control_layout = QHBoxLayout()
        self.run_btn = QPushButton('Run Clustering')

        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.hide()

        self.new_analysis_btn = QPushButton('New Cluster Analysis')
        self.new_analysis_btn.hide()

        self.run_control_layout.addWidget(self.run_btn)
        self.run_control_layout.addWidget(self.cancel_btn)
        self.run_control_layout.addWidget(self.new_analysis_btn)

    def setup_results_area(self):
        self.results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align widgets to the top

        # Progress bars
        self.progress_widget = QWidget()
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Loading embedding model...")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        self.progress_widget.setLayout(progress_layout)
        
        results_layout.addWidget(
            self.progress_widget,
            alignment=Qt.AlignmentFlag.AlignTop
            )
        self.progress_widget.hide()

        # Results summary
        self.results_label = QLabel("Run clustering to see results.")
        self.results_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
            )
        results_layout.addWidget(
            self.results_label,
            alignment=Qt.AlignmentFlag.AlignTop
            )

        # Visualization
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
            )
        self.web_view.setMinimumSize(440, 300)
        self.web_view.hide()
        results_layout.addWidget(self.web_view)

        self.results_group.setLayout(results_layout)

    def setup_export_area(self):
        self.export_group = QGroupBox("Export Options")
        export_layout = QHBoxLayout()

        self.export_csv_btn = QPushButton("Export Clusters to CSV")
        export_layout.addWidget(self.export_csv_btn)

        self.export_html_btn = QPushButton("Export Graphic to HTML")
        export_layout.addWidget(self.export_html_btn)

        self.export_group.setLayout(export_layout)

        self.export_group.hide()
