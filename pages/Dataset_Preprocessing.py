import streamlit as st
import pandas as pd
import numpy as np
import PIL.Image as Image

# Config
page_icon = Image.open("./assets/icon.ico")
st.set_page_config(layout="centered", page_title="AutoVision - Train your own ML model", page_icon=page_icon)

if 'df' not in st.session_state:
    st.session_state.df = None

if "delete_features" not in st.session_state:
    st.session_state.delete_features = None

if "missing_done" not in st.session_state:
    st.session_state.missing_done = False

if "cat_enc_done" not in st.session_state:
    st.session_state.cat_enc_done = False

if "num_scale_done" not in st.session_state:
    st.session_state.num_scale_done = False

if "split_done" not in st.session_state:
    st.session_state.split_done = False

if "X_train" not in st.session_state:
    st.session_state.X_train = None

if "X_test" not in st.session_state:
    st.session_state.X_test = None

if "y_train" not in st.session_state:
    st.session_state.y_train = None

if "y_test" not in st.session_state:
    st.session_state.y_test = None

if "X_val" not in st.session_state:
    st.session_state.X_val = None

if "y_val" not in st.session_state:
    st.session_state.y_val = None

if "split_type" not in st.session_state:
    st.session_state.split_type = None

if "build_model_done" not in st.session_state:
    st.session_state.build_model_done = False

if "no_svm" not in st.session_state:
    st.session_state.no_svm = False


def new_line():
    st.write("\n")


st.markdown("<h1 style='text-align: center; '>Dataset PreProcessing</h1>", unsafe_allow_html=True)
st.markdown("AutoVision is a tool that helps you to build a Machine Learning model in just a few clicks.",
            unsafe_allow_html=True)
st.divider()

st.header("Upload Your CSV File", anchor=False)
uploaded_file = st.file_uploader("Upload Your CSV File", type=["csv"])
st.divider()

if uploaded_file:

    # Read the CSV File
    if st.session_state.df is None:
        df = pd.read_csv(uploaded_file)
    else:
        df = st.session_state.df
        # st.dataframe(df)
        new_line()

    # The Dataset
    st.subheader("🎬 Dataset", anchor=False)
    new_line()
    st.dataframe(df, use_container_width=True)
    new_line()

    # Delete Features from the dataset
    st.subheader("🗑️ Delete Features", anchor=False)
    new_line()
    if not st.session_state.delete_features:
        delete_features = st.multiselect('Configure the features you want to delete from the dataset',
                                         df.columns.tolist())
        new_line()
        if delete_features:
            col1, col2, col3 = st.columns([1, 0.5, 1])
            if col2.button("Apply", key="delete"):
                st.session_state.delete_features = True
                st.session_state.df = df.drop(delete_features, axis=1)

    if st.session_state.delete_features:
        st.success("Features deleted successfully. You can now proceed to Handling Missing Values.")

    # Missing Values
    st.subheader("⚠️ Missing Values", anchor=False)
    if sum(df.isnull().sum().values.tolist()) != 0:
        new_line()
        # st.warning("There are missing values in the dataset. Please handle them before proceeding.")
        new_line()

        col1, col2 = st.columns(2)
        col1.markdown("<h6 style='text-align: center; '>Handling Numerical Features</h3>", unsafe_allow_html=True)
        col1.write("\n")
        missing_num_meth = col1.selectbox("Select the method to handle missing values in numerical features",
                                          ["Mean", "Median", "Mode", "ffil and bfil", "Drop the rows"])
        if df.select_dtypes(include=np.number).columns.tolist():
            num_feat = df.select_dtypes(include=np.number).columns.tolist()

        col2.markdown("<h6 style='text-align: center; '>Handling Categorical Features</h3>", unsafe_allow_html=True)
        col2.write("\n")
        missing_cat_meth = col2.selectbox("Select the method to handle missing values in categorical features",
                                          ["Mode", "Drop the rows"])
        if df.select_dtypes(include=object).columns.tolist():
            cat_feat = df.select_dtypes(include=object).columns.tolist()

        new_line()

        if missing_num_meth and missing_cat_meth:
            cola, colb, colc = st.columns([1, 0.5, 1])
            if colb.button("Apply", key="missing"):
                st.session_state.missing_done = True
                # If Numerical Features are present
                if df.select_dtypes(include=np.number).columns.tolist():
                    if missing_num_meth == "Mean":
                        from sklearn.impute import SimpleImputer

                        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
                        df[num_feat] = imputer.fit_transform(df[num_feat])
                        st.session_state.df = df

                    elif missing_num_meth == "Median":
                        from sklearn.impute import SimpleImputer

                        imputer = SimpleImputer(missing_values=np.nan, strategy='median')
                        df[num_feat] = imputer.fit_transform(df[num_feat])
                        st.session_state.df = df

                    elif missing_num_meth == "Mode":
                        from sklearn.impute import SimpleImputer

                        imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
                        df[num_feat] = imputer.fit_transform(df[num_feat])
                        st.session_state.df = df

                    elif missing_num_meth == "ffil and bfil":
                        df[num_feat] = df[num_feat].fillna(method='ffill').fillna(method='bfill')
                        st.session_state.df = df

                    elif missing_num_meth == "Drop the rows":
                        df[num_feat].dropna(inplace=True)
                        st.session_state.df = df

                # If Categorical Features are present
                if df.select_dtypes(include=object).columns.tolist():

                    if missing_cat_meth == "Mode":
                        from sklearn.impute import SimpleImputer

                        imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
                        df[cat_feat] = imputer.fit_transform(df[cat_feat])
                        st.session_state.df = df

                    elif missing_cat_meth == "Drop the rows":
                        df[cat_feat].dropna(inplace=True)
                        st.session_state.df = df

                st.success("Missing values handled successfully. You can now proceed to Encoding Categorical Features.")
    else:
        st.session_state.missing_done = True
        st.success("No missing values found in the dataset.")

    # Encoding Categorical Features
    if st.session_state.missing_done:
        new_line()
        st.subheader("☢️ Encoding Categorical Features", anchor=False)
        new_line()

        if len(df.select_dtypes(include=object).columns.tolist()) > 0:
            # st.warning("There are categorical features in the dataset. Please encode them before proceeding.")
            new_line()

            st.markdown("<h6 style='text-align: center; '>Select the method to encode categorical features</h3>",
                        unsafe_allow_html=True)
            new_line()
            cat_enc_meth = st.selectbox("Select the method to encode categorical features",
                                        ["Ordinal Encoding", "One Hot Encoding", "Count Frequency Encoding"])
            new_line()

            if cat_enc_meth:
                col1, col2, col3 = st.columns([1, 0.5, 1])
                if col2.button("Apply", key="cat_enc"):
                    st.session_state.cat_enc_done = True
                    cat_cols = df.select_dtypes(include=object).columns.tolist()

                    if cat_enc_meth == "Ordinal Encoding":
                        from sklearn.preprocessing import OrdinalEncoder

                        oe = OrdinalEncoder()
                        df[cat_cols] = oe.fit_transform(df[cat_cols])
                        st.session_state.df = df

                    elif cat_enc_meth == "One Hot Encoding":
                        df = pd.get_dummies(df, columns=cat_cols)
                        st.session_state.df = df

                    elif cat_enc_meth == "Count Frequency Encoding":
                        for col in cat_cols:
                            df[col] = df[col].map(df[col].value_counts() / len(df))
                        st.session_state.df = df

                    st.success(
                        "Categorical features encoded successfully. You can now proceed to Scaling & Transformation.")

        else:
            st.session_state.cat_enc_done = True
            st.success("No categorical features found in the dataset.")

    # Scaling & Transforming Numerical Features
    if st.session_state.cat_enc_done and st.session_state.missing_done:
        new_line()
        st.subheader("🧬 Scaling & Transformation", anchor=False)
        new_line()

        if not st.session_state.num_scale_done:
            if len(df.select_dtypes(include=np.number).columns.tolist()) > 0:
                # st.info("There are numerical features in the dataset. You can Scale and Transform them.")
                new_line()

                st.markdown(
                    "<h6 style='text-align: left; '>Select the method to scale and transform numerical features</h3>",
                    unsafe_allow_html=True)
                new_line()
                col1, col2 = st.columns(2)
                not_scale = col1.multiselect(
                    "Select the features you **don't** want to scale and transform **__Include the target feature if "
                    "it is Classification problem__**",
                    df.select_dtypes(include=np.number).columns.tolist())
                num_scale_meth = col2.selectbox("Select the method to scale and transform numerical features",
                                                ["Standard Scaler", "MinMax Scaler", "Robust Scaler",
                                                 "Log Transformation", "Square Root Transformation"])
                new_line()

                if num_scale_meth:
                    col1, col2, col3 = st.columns([1, 0.5, 1])
                    if col2.button("Apply", key="num_scale"):
                        st.session_state.num_scale_done = True
                        if not_scale:
                            num_cols = df.select_dtypes(include=np.number).columns.tolist()
                            # Delete the features that are not selected
                            for not_scale_feat in not_scale:
                                num_cols.remove(not_scale_feat)

                        else:
                            num_cols = df.select_dtypes(include=np.number).columns.tolist()

                        if num_scale_meth == "Standard Scaler":
                            from sklearn.preprocessing import StandardScaler

                            ss = StandardScaler()
                            df[num_cols] = ss.fit_transform(df[num_cols])
                            st.session_state.df = df

                        elif num_scale_meth == "MinMax Scaler":
                            from sklearn.preprocessing import MinMaxScaler

                            mms = MinMaxScaler()
                            df[num_cols] = mms.fit_transform(df[num_cols])
                            st.session_state.df = df

                        elif num_scale_meth == "Robust Scaler":
                            from sklearn.preprocessing import RobustScaler

                            rs = RobustScaler()
                            df[num_cols] = rs.fit_transform(df[num_cols])
                            st.session_state.df = df

                        elif num_scale_meth == "Log Transformation":
                            df[num_cols] = np.log(df[num_cols])
                            st.session_state.df = df

                        elif num_scale_meth == "Square Root Transformation":
                            df[num_cols] = np.sqrt(df[num_cols])
                            st.session_state.df = df

                        st.success(
                            "Numerical features scaled and transformed successfully. You can now proceed to Splitting"
                            "the dataset.")
            else:
                st.warning(
                    "No numerical features found in the dataset. There is something wrong with the dataset. Please"
                    "check it again.")
        else:
            st.session_state.num_scale_done = True
            st.success(
                "Numerical features scaled and transformed successfully. You can now proceed to Splitting the dataset.")

    # Splitting the dataset
    if st.session_state.cat_enc_done and st.session_state.missing_done:
        new_line()
        st.subheader("Splitting the dataset", anchor=False)
        new_line()

        if not st.session_state.split_done:
            # st.info("You can now split the dataset into Train, Validation and Test sets.")
            new_line()

            col1, col2 = st.columns(2)
            target = col1.selectbox("Select the target variable", df.columns.tolist())
            sets = col2.selectbox("Select the type of split", ["Train and Test", "Train, Validation and Test"])
            st.session_state.split_type = sets
            col1, col2, col3 = st.columns([1, 0.5, 1])
            if col2.button("Apply", key="split"):
                st.session_state.split_done = True

                if sets == "Train and Test":
                    from sklearn.model_selection import train_test_split

                    X = df.drop(target, axis=1)
                    y = df[target]
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                    st.session_state.X_train = X_train
                    st.session_state.X_test = X_test
                    st.session_state.y_train = y_train
                    st.session_state.y_test = y_test
                    st.success("Dataset split successfully. You can now proceed to Building the model.")

                elif sets == "Train, Validation and Test":
                    from sklearn.model_selection import train_test_split

                    X = df.drop(target, axis=1)
                    y = df[target]
                    X_train, X_rem, y_train, y_rem = train_test_split(X, y, test_size=0.3, random_state=42)
                    X_test, X_val, y_test, y_val = train_test_split(X_rem, y_rem, test_size=0.5, random_state=42)
                    st.session_state.X_train = X_train
                    st.session_state.X_test = X_test
                    st.session_state.X_val = X_val
                    st.session_state.y_train = y_train
                    st.session_state.y_test = y_test
                    st.session_state.y_val = y_val
                    st.success("Dataset split successfully. You can now proceed to Building the model.")

        else:
            if len(str(st.session_state.split_type).split()) == 4:
                st.success(
                    "Dataset split successfully into Training, Validation and Test sets. You can now proceed to "
                    "Building the model.")

            elif len(st.session_state.split_type.split()) == 3:
                st.success(
                    "Dataset split successfully into Training and Test sets. You can now proceed to Building the model.")

    # Building the model
    if st.session_state.split_done:
        new_line()
        st.subheader("Building the model", anchor=False)
        target, problem_type, model = None, None, None
        new_line()

        col1, col2, col3 = st.columns(3)
        target = col1.selectbox("Select the target variable", df.columns.tolist(), key="target_model")
        problem_type = col2.selectbox("Select the problem type", ["Classification", "Regression"])
        if problem_type == "Classification":
            model = col3.selectbox("Select the model",
                                   ["Logistic Regression", "K Nearest Neighbors", "Support Vector Machine",
                                    "Decision Tree", "Random Forest", "XGBoost", "LightGBM", "CatBoost"])
        elif problem_type == "Regression":
            model = col3.selectbox("Select the model",
                                   ["Linear Regression", "K Nearest Neighbors", "Support Vector Machine",
                                    "Decision Tree", "Random Forest", "XGBoost", "LightGBM", "CatBoost"])

        new_line()
        if target and problem_type and model:
            col1, col2, col3 = st.columns([1, 0.8, 1])
            if col2.button("Apply", key="build_model", use_container_width=True):
                st.session_state.build_model_done = True
                if problem_type == "Classification":

                    if model == "Logistic Regression":
                        from sklearn.linear_model import LogisticRegression
                        import pickle

                        lr = LogisticRegression()
                        lr.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(lr, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_log_reg',
                                             use_container_width=True)

                    elif model == "K Nearest Neighbors":
                        from sklearn.neighbors import KNeighborsClassifier
                        import pickle

                        knn = KNeighborsClassifier()
                        knn.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(knn, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_knn',
                                             use_container_width=True)

                    elif model == "Support Vector Machine":
                        from sklearn.svm import SVC
                        import pickle

                        st.session_state.no_svm = True

                        svm = SVC()
                        svm.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(svm, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_svm',
                                             use_container_width=True)

                    elif model == "Decision Tree":
                        from sklearn.tree import DecisionTreeClassifier
                        import pickle

                        dt = DecisionTreeClassifier()
                        dt.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(dt, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_dt',
                                             use_container_width=True)

                    elif model == "Random Forest":
                        from sklearn.ensemble import RandomForestClassifier
                        import pickle

                        rf = RandomForestClassifier()
                        rf.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(rf, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_rf',
                                             use_container_width=True)

                    elif model == "XGBoost":
                        from xgboost import XGBClassifier
                        import pickle

                        xgb = XGBClassifier()
                        xgb.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(xgb, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_xgb',
                                             use_container_width=True)

                    elif model == "LightGBM":
                        from lightgbm import LGBMClassifier
                        import pickle

                        lgbm = LGBMClassifier()
                        lgbm.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(lgbm, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_lgbm',
                                             use_container_width=True)

                    elif model == "CatBoost":
                        from catboost import CatBoostClassifier
                        import pickle

                        cb = CatBoostClassifier()
                        cb.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(cb, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key='class_cb',
                                             use_container_width=True)

                elif problem_type == "Regression":

                    if model == "Linear Regression":
                        from sklearn.linear_model import LinearRegression
                        import pickle

                        lr = LinearRegression()
                        lr.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(lr, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key="reg_lin_reg",
                                             use_container_width=True)

                    elif model == "K Nearest Neighbors":
                        from sklearn.neighbors import KNeighborsRegressor
                        import pickle

                        knn = KNeighborsRegressor()
                        knn.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(knn, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key="reg_knn",
                                             use_container_width=True)

                    elif model == "Support Vector Machine":
                        from sklearn.svm import SVR
                        import pickle

                        svm = SVR()
                        svm.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(svm, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key="reg_svm",
                                             use_container_width=True)

                    elif model == "Decision Tree":
                        from sklearn.tree import DecisionTreeRegressor
                        import pickle

                        dt = DecisionTreeRegressor()
                        dt.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(dt, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button("Download Model", model_bytes, "model.pkl", key="reg_dt",
                                             use_container_width=True)

                    elif model == "Random Forest":
                        from sklearn.ensemble import RandomForestRegressor
                        import pickle

                        rf = RandomForestRegressor()
                        rf.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(rf, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open("model.pkl", "rb")
                        model_bytes = model_file.read()
                        col2.download_button('Download Model', model_bytes, 'model.pkl', key="reg_rf",
                                             use_container_width=True)

                    elif model == "XGBoost":
                        from xgboost import XGBRegressor
                        import pickle

                        xgb = XGBRegressor()
                        xgb.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(xgb, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open('model.pkl', 'rb')
                        model_bytes = model_file.read()
                        col2.download_button('Download Model', model_bytes, 'model.pkl', key="reg_xgb",
                                             use_container_width=True)

                    elif model == "LightGBM":
                        from lightgbm import LGBMRegressor
                        import pickle

                        lgbm = LGBMRegressor()
                        lgbm.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(lgbm, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open('model.pkl', 'rb')
                        model_bytes = model_file.read()
                        col2.download_button('Download Model', model_bytes, 'model.pkl', key="reg_lgbm",
                                             use_container_width=True)

                    elif model == "CatBoost":
                        from catboost import CatBoostRegressor
                        import pickle

                        cb = CatBoostRegressor()
                        cb.fit(st.session_state.X_train, st.session_state.y_train)

                        pickle.dump(cb, open('model.pkl', 'wb'))
                        st.success("Model built successfully. You can now proceed to Evaluation.")

                        model_file = open('model.pkl', 'rb')
                        model_bytes = model_file.read()
                        col2.download_button('Download Model', model_bytes, 'model.pkl', key="reg_cb",
                                             use_container_width=True)

    # # Evaluation
    if st.session_state.build_model_done:
        new_line()
        st.subheader("Evaluation", anchor=False)
        new_line()
        # with st.expander("Show Evaluation Metrics"):
        if st.session_state.split_type == "Train and Test":

            if problem_type == "Classification":
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, \
                    confusion_matrix
                import pickle

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)
                if not st.session_state.no_svm:
                    y_prob = model.predict_proba(st.session_state.X_test)[:, 1]

                # Dataframe to store the metrics values for each set
                metrics_df = pd.DataFrame(columns=["Accuracy", "Precision", "Recall", "F1", "ROC AUC"],
                                          index=["Train", "Test"])
                metrics_df.loc["Train", "Accuracy"] = accuracy_score(st.session_state.y_train,
                                                                     model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "Precision"] = precision_score(st.session_state.y_train,
                                                                       model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "Recall"] = recall_score(st.session_state.y_train,
                                                                 model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "F1"] = f1_score(st.session_state.y_train,
                                                         model.predict(st.session_state.X_train))
                if not st.session_state.no_svm:
                    metrics_df.loc["Train", "ROC AUC"] = roc_auc_score(st.session_state.y_train,
                                                                       model.predict_proba(st.session_state.X_train)[:,
                                                                       1])
                metrics_df.loc["Test", "Accuracy"] = accuracy_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Precision"] = precision_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Recall"] = recall_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "F1"] = f1_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "ROC AUC"] = roc_auc_score(st.session_state.y_test, y_prob)

                new_line()

                # Plot the other metrics using plotly
                st.markdown("#### Metrics Plot")
                import plotly.graph_objects as go

                fig = go.Figure(data=[
                    go.Bar(name='Train', x=metrics_df.columns.tolist(), y=metrics_df.loc["Train", :].values.tolist()),
                    go.Bar(name='Test', x=metrics_df.columns.tolist(), y=metrics_df.loc["Test", :].values.tolist())
                ])
                st.plotly_chart(fig)

                # Plot the ROC Curve using px
                import plotly.express as px
                from sklearn.metrics import roc_curve

                fpr, tpr, thresholds = roc_curve(st.session_state.y_test, y_prob)
                fig = px.area(
                    x=fpr, y=tpr,
                    title=f'ROC Curve (AUC={metrics_df.loc["Test", "ROC AUC"]:.4f})',
                    labels=dict(x='False Positive Rate', y='True Positive Rate'),
                    width=400, height=500
                )
                fig.add_shape(
                    type='line', line=dict(dash='dash'),
                    x0=0, x1=1, y0=0, y1=1
                )

                fig.update_yaxes(scaleanchor="x", scaleratio=1)
                fig.update_xaxes(constrain='domain')
                st.plotly_chart(fig)

                # Display the metrics values
                new_line()
                st.markdown("##### Metrics Values")
                st.write(metrics_df)

                # Plot confusion matrix as plot with plot_confusion_matrix
                # from sklearn.metrics import plot_confusion_matrix
                import matplotlib.pyplot as plt
                from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

                st.markdown("#### Confusion Matrix")
                new_line()

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)

                # cm = confusion_matrix(y_test, y_pred_test)
                fig, ax = plt.subplots(figsize=(6, 6))
                ConfusionMatrixDisplay.from_predictions(st.session_state.y_test, y_pred, ax=ax)
                st.pyplot(fig)

            elif problem_type == "Regression":
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                import pickle

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)

                # Dataframe to store the metrics values for each set with RMSE
                metrics_df = pd.DataFrame(columns=["Mean Squared Error", "Mean Absolute Error", "R2 Score"],
                                          index=["Train", "Test"])
                metrics_df.loc["Train", "Mean Squared Error"] = mean_squared_error(st.session_state.y_train,
                                                                                   model.predict(
                                                                                       st.session_state.X_train))
                metrics_df.loc["Train", "Mean Absolute Error"] = mean_absolute_error(st.session_state.y_train,
                                                                                     model.predict(
                                                                                         st.session_state.X_train))
                metrics_df.loc["Train", "R2 Score"] = r2_score(st.session_state.y_train,
                                                               model.predict(st.session_state.X_train))
                metrics_df.loc['Train', 'RMSE'] = np.sqrt(metrics_df.loc['Train', 'Mean Squared Error'])
                metrics_df.loc["Test", "Mean Squared Error"] = mean_squared_error(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Mean Absolute Error"] = mean_absolute_error(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "R2 Score"] = r2_score(st.session_state.y_test, y_pred)
                metrics_df.loc['Test', 'RMSE'] = np.sqrt(metrics_df.loc['Test', 'Mean Squared Error'])

                new_line()

                # Plot the other metrics using plotly
                st.markdown("#### Metrics Plot")
                import plotly.graph_objects as go

                fig = go.Figure(data=[
                    go.Bar(name='Train', x=metrics_df.columns.tolist(), y=metrics_df.loc["Train", :].values.tolist()),
                    go.Bar(name='Test', x=metrics_df.columns.tolist(), y=metrics_df.loc["Test", :].values.tolist())
                ])
                st.plotly_chart(fig)

                # Display the metrics values
                new_line()
                st.markdown("##### Metrics Values")
                st.write(metrics_df)

        elif st.session_state.split_type == "Train, Validation and Test":

            if problem_type == "Classification":

                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, \
                    confusion_matrix
                import pickle

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)
                if not st.session_state.no_svm:
                    y_prob = model.predict_proba(st.session_state.X_test)[:, 1]

                # Dataframe to store the metrics values for each set
                metrics_df = pd.DataFrame(columns=["Accuracy", "Precision", "Recall", "F1", "ROC AUC"],
                                          index=["Train", "Validation", "Test"])
                metrics_df.loc["Train", "Accuracy"] = accuracy_score(st.session_state.y_train,
                                                                     model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "Precision"] = precision_score(st.session_state.y_train,
                                                                       model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "Recall"] = recall_score(st.session_state.y_train,
                                                                 model.predict(st.session_state.X_train))
                metrics_df.loc["Train", "F1"] = f1_score(st.session_state.y_train,
                                                         model.predict(st.session_state.X_train))
                if not st.session_state.no_svm:
                    metrics_df.loc["Train", "ROC AUC"] = roc_auc_score(st.session_state.y_train,
                                                                       model.predict_proba(st.session_state.X_train)[:,
                                                                       1])
                metrics_df.loc["Validation", "Accuracy"] = accuracy_score(st.session_state.y_val,
                                                                          model.predict(st.session_state.X_val))
                metrics_df.loc["Validation", "Precision"] = precision_score(st.session_state.y_val,
                                                                            model.predict(st.session_state.X_val))
                metrics_df.loc["Validation", "Recall"] = recall_score(st.session_state.y_val,
                                                                      model.predict(st.session_state.X_val))
                metrics_df.loc["Validation", "F1"] = f1_score(st.session_state.y_val,
                                                              model.predict(st.session_state.X_val))
                if not st.session_state.no_svm:
                    metrics_df.loc["Validation", "ROC AUC"] = roc_auc_score(st.session_state.y_val,
                                                                            model.predict_proba(st.session_state.X_val)[
                                                                            :, 1])
                metrics_df.loc["Test", "Accuracy"] = accuracy_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Precision"] = precision_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Recall"] = recall_score(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "F1"] = f1_score(st.session_state.y_test, y_pred)
                if not st.session_state.no_svm:
                    metrics_df.loc["Test", "ROC AUC"] = roc_auc_score(st.session_state.y_test, y_prob)

                new_line()

                # Plot the other metrics using plotly
                st.markdown("#### Metrics Plot")
                import plotly.graph_objects as go

                fig = go.Figure(data=[
                    go.Bar(name='Train', x=metrics_df.columns.tolist(), y=metrics_df.loc["Train", :].values.tolist()),
                    go.Bar(name='Validation', x=metrics_df.columns.tolist(),
                           y=metrics_df.loc["Validation", :].values.tolist()),
                    go.Bar(name='Test', x=metrics_df.columns.tolist(), y=metrics_df.loc["Test", :].values.tolist())
                ])
                st.plotly_chart(fig)

                # Plot the ROC Curve using px
                if not st.session_state.no_svm:
                    import plotly.express as px
                    from sklearn.metrics import roc_curve

                    fpr, tpr, thresholds = roc_curve(st.session_state.y_test, y_prob)
                    fig = px.area(
                        x=fpr, y=tpr,
                        title=f'ROC Curve (AUC={metrics_df.loc["Test", "ROC AUC"]:.4f})',
                        labels=dict(x='False Positive Rate', y='True Positive Rate'),
                        width=400, height=500
                    )
                    fig.add_shape(
                        type='line', line=dict(dash='dash'),
                        x0=0, x1=1, y0=0, y1=1
                    )

                    fig.update_yaxes(scaleanchor="x", scaleratio=1)
                    fig.update_xaxes(constrain='domain')
                    st.plotly_chart(fig)

                # Display the metrics values
                new_line()
                st.markdown("##### Metrics Values")
                st.write(metrics_df)

                # Plot confusion matrix as plot with plot_confusion_matrix
                # from sklearn.metrics import plot_confusion_matrix
                import matplotlib.pyplot as plt

                from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

                st.markdown("#### Confusion Matrix")
                new_line()

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)

                # cm = confusion_matrix(y_test, y_pred_test)
                fig, ax = plt.subplots(figsize=(6, 6))
                ConfusionMatrixDisplay.from_predictions(st.session_state.y_test, y_pred, ax=ax)
                st.pyplot(fig)

            elif problem_type == "Regression":

                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                import pickle

                model = pickle.load(open('model.pkl', 'rb'))
                y_pred = model.predict(st.session_state.X_test)

                # Dataframe to store the metrics values for each set with RMSE
                metrics_df = pd.DataFrame(columns=["Mean Squared Error", "Mean Absolute Error", "R2 Score"],
                                          index=["Train", "Validation", "Test"])
                metrics_df.loc["Train", "Mean Squared Error"] = mean_squared_error(st.session_state.y_train,
                                                                                   model.predict(
                                                                                       st.session_state.X_train))
                metrics_df.loc["Train", "Mean Absolute Error"] = mean_absolute_error(st.session_state.y_train,
                                                                                     model.predict(
                                                                                         st.session_state.X_train))
                metrics_df.loc["Train", "R2 Score"] = r2_score(st.session_state.y_train,
                                                               model.predict(st.session_state.X_train))
                metrics_df.loc['Train', 'RMSE'] = np.sqrt(metrics_df.loc['Train', 'Mean Squared Error'])
                metrics_df.loc["Validation", "Mean Squared Error"] = mean_squared_error(st.session_state.y_val,
                                                                                        model.predict(
                                                                                            st.session_state.X_val))
                metrics_df.loc["Validation", "Mean Absolute Error"] = mean_absolute_error(st.session_state.y_val,
                                                                                          model.predict(
                                                                                              st.session_state.X_val))
                metrics_df.loc["Validation", "R2 Score"] = r2_score(st.session_state.y_val,
                                                                    model.predict(st.session_state.X_val))
                metrics_df.loc['Validation', 'RMSE'] = np.sqrt(metrics_df.loc['Validation', 'Mean Squared Error'])
                metrics_df.loc["Test", "Mean Squared Error"] = mean_squared_error(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "Mean Absolute Error"] = mean_absolute_error(st.session_state.y_test, y_pred)
                metrics_df.loc["Test", "R2 Score"] = r2_score(st.session_state.y_test, y_pred)
                metrics_df.loc['Test', 'RMSE'] = np.sqrt(metrics_df.loc['Test', 'Mean Squared Error'])

                new_line()

                # Plot the other metrics using plotly
                st.markdown("#### Metrics Plot")
                import plotly.graph_objects as go

                fig = go.Figure(data=[
                    go.Bar(name='Train', x=metrics_df.columns.tolist(), y=metrics_df.loc["Train", :].values.tolist()),
                    go.Bar(name='Validation', x=metrics_df.columns.tolist(),
                           y=metrics_df.loc["Validation", :].values.tolist()),
                    go.Bar(name='Test', x=metrics_df.columns.tolist(), y=metrics_df.loc["Test", :].values.tolist())
                ])
                st.plotly_chart(fig)

                # Display the metrics values
                new_line()
                st.markdown("##### Metrics Values")
                st.write(metrics_df)
