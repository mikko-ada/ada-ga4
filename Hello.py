import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import csv
import openai
openai.api_key = "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"


st.title("GA4 Analytics")

tab2, tab3, tab4 = st.tabs(["Purchase Funnel", "Traffic", "SKU"])

def call_openai(content):
    return openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a seasoned marketer, that provides insights given data from Google Analytics"},
                {"role": "user", "content": content}
            ],
            temperature=0.7
        )["choices"][0]["message"]["content"]



with tab2:
    st.header("Purchase Funnel")

    purchase_funnel_file = st.file_uploader("Upload your purchase funnel CSV file")
    purchase_funnel_file_raw = st.file_uploader("Or your raw Looker purchase funnel CSV file here")

    st.divider()

    if purchase_funnel_file_raw:
        df_2 = pd.read_csv(purchase_funnel_file_raw, parse_dates=['Date'], dtype={'Event count': float})
        df_2['Date'] = pd.to_datetime(df_2['Date']).dt.date
        st.header("All events")
        start_date_1 = st.date_input("Base Start Date")
        end_date_1 = st.date_input("Base End Date")
        start_date_2 = st.date_input("Comparing Start Date")
        end_date_2 = st.date_input("Comparing End Date")
        all_events = df_2["Event name"]
        stage1event = st.selectbox("Stage 1 Event", df_2["Event name"].unique().tolist(), index=df_2["Event name"].unique().tolist().index("session_start"))
        stage2event = st.selectbox("Stage 2 Event", df_2["Event name"].unique().tolist(), index=df_2["Event name"].unique().tolist().index("add_to_cart"))
        stage3event = st.selectbox("Stage 3 Event", df_2["Event name"].unique().tolist(), index=df_2["Event name"].unique().tolist().index("begin_checkout"))
        stage4event = st.selectbox("Stage 4 Event", df_2["Event name"].unique().tolist(), index=df_2["Event name"].unique().tolist().index("purchase"))
        before_df = df_2[(df_2["Date"] <= end_date_1) & (df_2["Date"] >= start_date_1)]
        after_df = df_2[(df_2["Date"] <= end_date_2) & (df_2["Date"] >= start_date_2)]
        st.subheader(f"Data from: {start_date_1} to {end_date_1}")
        before_pt = pd.pivot_table(before_df, columns=["Event name"], index=["Device category"], values="Event count", aggfunc="sum")[[stage1event, stage2event, stage3event, stage4event]]
        before_pt1 = before_pt.iloc[:, 0:-1]
        before_pt1.columns = [f"Drop off {num}" for num in list(range(1, before_pt1.shape[1] + 1))]
        before_pt2 = before_pt.iloc[:, 1:]
        before_pt2.columns = [f"Drop off {num}" for num in list(range(1, before_pt2.shape[1] + 1))]
        st.write("Sessions for every step")
        st.write(before_pt)
        st.write("Drop offs for every step")
        before_dropoff = before_pt1 - before_pt2
        before_dropoff_p = ((before_pt1 - before_pt2) / before_pt1 * 100).round(2)
        before_fig = go.Figure(data=go.Heatmap(
            z=before_dropoff_p,
            x=before_dropoff_p.columns,
            y=before_dropoff_p.index,
            text="Total drop off: " + before_dropoff.astype(
                str) + "<br>" + "% drop off: " + before_dropoff_p.astype(str) + "%",
            texttemplate="%{text}",
        ))
        st.write(before_fig)
        st.subheader(f"Data from: {start_date_2} to {end_date_2}")
        after_pt = pd.pivot_table(after_df, columns=["Event name"], index=["Device category"], values="Event count", aggfunc="sum")[[stage1event, stage2event, stage3event, stage4event]]
        after_pt1 = after_pt.iloc[:, 0:-1]
        after_pt1.columns = [f"Drop off {num}" for num in list(range(1, after_pt1.shape[1] + 1))]
        after_pt2 = after_pt.iloc[:, 1:]
        after_pt2.columns = [f"Drop off {num}" for num in list(range(1, after_pt2.shape[1] + 1))]
        st.write("Sessions for every step")
        st.write(after_pt)
        st.write("Drop offs for every step")
        after_dropoff = after_pt1 - after_pt2
        after_dropoff_p = ((after_pt1 - after_pt2) / after_pt1 * 100).round(2)
        after_fig = go.Figure(data=go.Heatmap(
            z=after_dropoff_p,
            x=after_dropoff_p.columns,
            y=after_dropoff_p.index,
            text="Total drop off: " + after_dropoff.astype(
                str) + "<br>" + "% drop off: " + after_dropoff_p.astype(str) + "%",
            texttemplate="%{text}",
        ))
        st.write(after_fig)
    if purchase_funnel_file:

        lines = [line.decode('utf-8') for line in purchase_funnel_file.readlines()]

        processed_lines = [line.split(',') for line in lines]  # Customize this as needed
        #df = pd.DataFrame(processed_lines)
        for index, line in enumerate(processed_lines):
            if "Start date:" in line[0]:

                st.subheader(f"Data from: {line[0][-10:-1]} to {processed_lines[index+1][0][-10:-1]}")
                for i, x in enumerate(processed_lines[index:]):
                    if len(x[0].strip()) == 0:
                        df = pd.DataFrame(processed_lines[index + 2: index + i])
                        #new_header = df.iloc[0]  # Grab the first row for the header
                        df = df[1:]  # Take the data less the header row
                        #df.columns = new_header  # Set the header row as the df header
                        df = df.set_index(df.columns[0])
                        df.index.name = 'category'  # Rename the index
                        df = df.iloc[:, 0::2]
                        df.columns = [f"Step {num}" for num in list(range(1, df.shape[1]+1))]
                        df = df.apply(pd.to_numeric, errors='coerce')
                        df1 = df.iloc[:, 0:-1]
                        df1.columns = [f"Drop off {num}" for num in list(range(1, df1.shape[1]+1))]
                        df2 = df.iloc[:, 1:]
                        df2.columns = [f"Drop off {num}" for num in list(range(1, df2.shape[1]+1))]
                        differences_df_earlier = df1 - df2
                        diff_p_df_earlier = ((df1 - df2) / df1 * 100).round(2)
                        fig = go.Figure(data=go.Heatmap(
                            z=diff_p_df_earlier,
                            x=diff_p_df_earlier.columns,
                            y=diff_p_df_earlier.index,
                            text="Total drop off: " + differences_df_earlier.astype(str) + "<br>" + "% drop off: " + diff_p_df_earlier.astype(str) + "%",
                            texttemplate="%{text}",
                            ))
                        st.write("Sessions for every step")
                        st.dataframe(df, use_container_width=True)
                        #st.write(differences_df)
                        #st.write(diff_p_df)
                        st.write("Drop offs for every step")
                        st.write(fig)
                        st.divider()
                        break
                    elif (index + i == len(processed_lines) - 1):
                        df = pd.DataFrame(processed_lines[index + 2: index + i + 1])
                        # new_header = df.iloc[0]  # Grab the first row for the header
                        df = df[1:]  # Take the data less the header row
                        # df.columns = new_header  # Set the header row as the df header
                        df = df.set_index(df.columns[0])
                        df.index.name = 'category'  # Rename the index
                        df = df.iloc[:, 0::2]
                        df.columns = [f"Step {num}" for num in list(range(1, df.shape[1] + 1))]
                        df = df.apply(pd.to_numeric, errors='coerce')
                        df1 = df.iloc[:, 0:-1]
                        df1.columns = [f"Drop off {num}" for num in list(range(1, df1.shape[1] + 1))]
                        df2 = df.iloc[:, 1:]
                        df2.columns = [f"Drop off {num}" for num in list(range(1, df2.shape[1] + 1))]
                        differences_df = df1 - df2
                        diff_p_df = ((df1 - df2) / df1 * 100).round(2)
                        fig = go.Figure(data=go.Heatmap(
                            z=diff_p_df,
                            x=diff_p_df.columns,
                            y=diff_p_df.index,
                            text="Total drop off: " + differences_df.astype(str) + "<br>" + "% drop off: " + diff_p_df.astype(
                                str) + "%",
                            texttemplate="%{text}",
                        ))
                        st.write("Sessions for every step")
                        st.dataframe(df, use_container_width=True)
                        # st.write(differences_df)
                        # st.write(diff_p_df)
                        st.write("Drop offs for every step")
                        st.write(fig)
        st.divider()
        st.subheader("Growth/drop between later time period and earlier time period")
        st.dataframe(diff_p_df_earlier - diff_p_df, use_container_width=True)
        fig_diff = go.Figure(data=go.Heatmap(
            z=(diff_p_df_earlier - diff_p_df),
            x=(diff_p_df_earlier - diff_p_df).columns,
            y=(diff_p_df_earlier - diff_p_df).index,
            text="Growth in drop off: " + (differences_df_earlier - differences_df).astype(str) + "<br>" + "% growth in drop off: " + (diff_p_df_earlier - diff_p_df).round(2).astype(
                str) + "%",
            texttemplate="%{text}",
        ))
        st.write(fig_diff)

with tab3:
    st.title("Traffic")
    traffic_file = st.file_uploader("Upload your traffic CSV file here")
    traffic_file_raw = st.file_uploader("or your raw Looker traffic CSV file here")
    st.divider()

    if traffic_file_raw:
        start_date_1 = st.date_input("Base Start Date")
        end_date_1 = st.date_input("Base End Date")
        start_date_2 = st.date_input("Comparing Start Date")
        end_date_2 = st.date_input("Comparing End Date")
        st.subheader(f"Data from: {start_date_1} to {end_date_1}")
        traffic_df_raw = pd.read_csv(traffic_file_raw)
        traffic_df_raw['Date'] = pd.to_datetime(traffic_df_raw['Date']).dt.date
        traffic_df_raw = traffic_df_raw.apply(pd.to_numeric, errors='ignore')
        before_df_traffic_raw = traffic_df_raw[(traffic_df_raw["Date"] <= end_date_1) & (traffic_df_raw["Date"] >= start_date_1)]
        after_df_traffic_raw = traffic_df_raw[(traffic_df_raw["Date"] <= end_date_2) & (traffic_df_raw["Date"] >= start_date_2)]
        # st.write(traffic_df)
        traffic_pt_before = pd.pivot_table(data=before_df_traffic_raw, index="First user source / medium",
                                    values=["Engaged sessions", "Conversions"], aggfunc="sum")
        traffic_pt_before["CR Ratio"] = (traffic_pt_before["Conversions"] / traffic_pt_before["Engaged sessions"]).round(2)
        filtered_pt_before = traffic_pt_before[traffic_pt_before["Engaged sessions"] > 100].sort_values(by="Engaged sessions",
                                                                                   ascending=False)
        # st.write(traffic_df)
        st.write(call_openai(
            f"This is a summary of source/medium with the conversions, engaged sessions, and conversion rate ratio. Provide summary and insights on how we can improve conversions and traffic. The dataframe is: {filtered_pt_before}"))
        st.dataframe(filtered_pt_before, use_container_width=True)
        sourcemed_fig_before = px.scatter(filtered_pt_before, x="Engaged sessions", y="CR Ratio",
                                     color=filtered_pt_before.index)
        st.write(sourcemed_fig_before)
        st.divider()
        st.subheader(f"Data from: {start_date_2} to {end_date_2}")
        traffic_pt_after = pd.pivot_table(data=after_df_traffic_raw, index="First user source / medium",
                                           values=["Engaged sessions", "Conversions"], aggfunc="sum")
        traffic_pt_after["CR Ratio"] = (
                    traffic_pt_after["Conversions"] / traffic_pt_after["Engaged sessions"]).round(2)
        filtered_pt_after = traffic_pt_after[traffic_pt_after["Engaged sessions"] > 100].sort_values(
            by="Engaged sessions",
            ascending=False)
        # st.write(traffic_df)
        st.write(call_openai(
            f"This is a summary of source/medium with the conversions, engaged sessions, and conversion rate ratio. Provide summary and insights on how we can improve conversions and traffic. The dataframe is: {filtered_pt_before}"))
        st.dataframe(filtered_pt_after, use_container_width=True)
        sourcemed_fig_after = px.scatter(filtered_pt_after, x="Engaged sessions", y="CR Ratio",
                                          color=filtered_pt_after.index)
        st.write(sourcemed_fig_after)
        st.divider()
        st.subheader("Comparison of source/medium between time periods (%)")
        traffic_difference_p_pt_raw = (filtered_pt_after - filtered_pt_before) / filtered_pt_after
        st.write(traffic_difference_p_pt_raw.sort_values(by="Engaged sessions", ascending=False))
        st.divider()
        st.subheader("Comparison of campaigns between time periods")
        sourcemed_option_raw = st.selectbox(
            'Select source/medium', filtered_pt_before.index)
        campaign_pt_before = pd.pivot_table(before_df_traffic_raw[before_df_traffic_raw["First user source / medium"] == sourcemed_option_raw],
                                     index="Session campaign",
                                     values=["Engaged sessions", "Conversions"],
                                     aggfunc="sum"
                                     )
        campaign_pt_before["CR Ratio"] = campaign_pt_before["Conversions"] / campaign_pt_before["Engaged sessions"]
        campaign_pt_after = pd.pivot_table(after_df_traffic_raw[after_df_traffic_raw["First user source / medium"] == sourcemed_option_raw],
                                       index="Session campaign",
                                       values=["Engaged sessions", "Conversions"],
                                       aggfunc="sum"
                                       )
        campaign_pt_after["CR Ratio"] = campaign_pt_after["Conversions"] / campaign_pt_after["Engaged sessions"]
        st.write(campaign_pt_after - campaign_pt_before)


    if traffic_file:

        traffic_lines = [line.decode('utf-8') for line in traffic_file.readlines()]
        traffic_reader = csv.reader(traffic_lines)
        traffic_processed_lines = list(traffic_reader)

        for index, line in enumerate(traffic_processed_lines):
            if "Start date:" in line[0]:
                st.subheader(f"{line[0][-8:]} to {traffic_processed_lines[index+1][0][-8:]}")
                for i, x in enumerate(traffic_processed_lines[index:]):
                    if len(x[0].strip()) == 0:
                        traffic_df = pd.DataFrame(traffic_processed_lines[index + 2: index + i])
                        new_header = traffic_df.iloc[0]  # Grab the first row for the header
                        traffic_df = traffic_df[1:]  # Take the data less the header row
                        traffic_df.columns = new_header  # Set the header row as the df header
                        traffic_df = traffic_df.apply(pd.to_numeric, errors='ignore')
                        #st.write(traffic_df)
                        traffic_pt = pd.pivot_table(data=traffic_df, index="First user source / medium", values=["Engaged sessions", "Conversions"], aggfunc="sum")
                        traffic_pt["CR Ratio"] = (traffic_pt["Conversions"] / traffic_pt["Engaged sessions"]).round(2)
                        filtered_pt = traffic_pt[traffic_pt["Engaged sessions"] > 100].sort_values(by="Engaged sessions", ascending=False)
                        #st.write(traffic_df)
                        st.write(call_openai(f"This is a summary of source/medium with the conversions, engaged sessions, and conversion rate ratio. Provide summary and insights on how we can improve conversions and traffic. The dataframe is: {filtered_pt}"))
                        st.dataframe(filtered_pt, use_container_width=True)
                        sourcemed_fig21 = px.scatter(filtered_pt, x="Engaged sessions", y="CR Ratio",
                                                    color=filtered_pt.index)
                        st.write(sourcemed_fig21)
                        st.divider()
                        break
                    elif (index + i == len(traffic_processed_lines) - 1):
                        traffic_df_2 = pd.DataFrame(traffic_processed_lines[index + 2: index + i])
                        new_header = traffic_df_2.iloc[0]  # Grab the first row for the header
                        traffic_df_2 = traffic_df_2[1:]  # Take the data less the header row
                        traffic_df_2.columns = new_header  # Set the header row as the df header
                        traffic_df_2 = traffic_df_2.apply(pd.to_numeric, errors='ignore')
                        traffic_pt_2 = pd.pivot_table(data=traffic_df_2, index="First user source / medium",
                                                    values=["Engaged sessions", "Conversions"], aggfunc="sum")
                        traffic_pt_2["CR Ratio"] = (traffic_pt_2["Conversions"] / traffic_pt_2["Engaged sessions"]).round(2)
                        filtered_pt_2 = traffic_pt_2[traffic_pt["Engaged sessions"] > 100].sort_values(by="Engaged sessions", ascending=False)
                        #st.write(traffic_df_2)
                        st.write(call_openai(f"This is a summary of source/medium with the conversions, engaged sessions, and conversion rate ratio. Provide summary and insights on how we can improve conversions and traffic. The dataframe is: {filtered_pt_2}"))
                        st.dataframe(filtered_pt_2, use_container_width=True)
                        sourcemed_fig22 = px.scatter(filtered_pt_2, x="Engaged sessions", y="CR Ratio",
                                                    color=filtered_pt_2.index)
                        st.write(sourcemed_fig22)
                        st.divider()
                        st.subheader("Comparison of source/medium between time periods (Absolute)")
                        traffic_difference_pt = filtered_pt - filtered_pt_2
                        st.write(call_openai(f"This is a summary of source/medium with the increase or decrease conversions, engaged sessions, and conversion rate ratio between 2 time periods. Provide summary and insights on how we can improve conversions and traffic. The dataframe is: {traffic_difference_pt}"))
                        st.dataframe(traffic_difference_pt.sort_values(by="Engaged sessions", ascending=False), use_container_width=True)
                        sourcemed_fig = go.Figure(
                            data=[
                                go.Scatter(
                                    x=filtered_pt_2["Engaged sessions"],
                                    y=filtered_pt_2.index,
                                    mode="markers",
                                    name="before",
                                    marker=dict(
                                        color="green",
                                        size=10
                                    )

                                ),
                                go.Scatter(
                                    x=filtered_pt["Engaged sessions"],
                                    y=filtered_pt.index,
                                    mode="markers",
                                    name="after",
                                    marker=dict(
                                        color="blue",
                                        size=10
                                    )
                                ),
                            ]
                        )
                        st.write(sourcemed_fig)
                        st.divider()

                        st.subheader("Comparison of source/medium between time periods (%)")
                        traffic_difference_p_pt = (filtered_pt - filtered_pt_2)/filtered_pt_2
                        st.write(traffic_difference_p_pt.sort_values(by="Engaged sessions", ascending=False))
                        st.divider()
                        st.subheader("Comparison of campaigns between time periods")
                        sourcemed_option = st.selectbox(
                            'Select source/medium', filtered_pt.index)
                        campaign_pt = pd.pivot_table(traffic_df[traffic_df["First user source / medium"] == sourcemed_option],
                                                     index="Session campaign",
                                                     values=["Engaged sessions", "Conversions"],
                                                     aggfunc="sum"
                                                     )
                        campaign_pt["CR Ratio"] = campaign_pt["Conversions"] / campaign_pt["Engaged sessions"]
                        campaign_pt_2 = pd.pivot_table(traffic_df_2[traffic_df_2["First user source / medium"] == sourcemed_option],
                                                     index="Session campaign",
                                                     values=["Engaged sessions", "Conversions"],
                                                     aggfunc="sum"
                                                     )
                        campaign_pt_2["CR Ratio"] = campaign_pt_2["Conversions"] / campaign_pt_2["Engaged sessions"]
                        st.write(campaign_pt - campaign_pt_2)

with tab4:
    st.title("SKU")
    sku_file = st.file_uploader("Upload your SKU CSV file")

    if sku_file:

        sku_lines = [line.decode('utf-8') for line in sku_file.readlines()]
        sku_reader = csv.reader(sku_lines)
        sku_processed_lines = list(sku_reader)

        for index, line in enumerate(sku_processed_lines):
            if "Start date:" in line[0]:
                st.subheader(line[0])
                st.subheader(sku_processed_lines[index+1][0])
                for i, x in enumerate(sku_processed_lines[index:]):
                    if len(x[0].strip()) == 0:
                        sku_df = pd.DataFrame(sku_processed_lines[index + 2: index + i])
                        new_header = sku_df.iloc[0]  # Grab the first row for the header
                        sku_df = sku_df[1:]  # Take the data less the header row
                        sku_df.columns = new_header  # Set the header row as the df header
                        sku_df = sku_df.apply(pd.to_numeric, errors='ignore')
                        #st.write(sku_df)
                        sku_pt = pd.pivot_table(data=sku_df, index="Item name", values=["Items viewed", "Items purchased"], aggfunc="sum")
                        sku_pt["CR Ratio"] = (sku_pt["Items purchased"] / sku_pt["Items viewed"]).round(2)
                        sku_filtered_pt = sku_pt[sku_pt["Items viewed"] > 100].sort_values(by="Items viewed", ascending=False)
                        st.write(sku_df)
                        st.write(sku_filtered_pt)
                        break
                    elif (index + i == len(sku_processed_lines) - 1):
                        sku_df_2 = pd.DataFrame(sku_processed_lines[index + 2: index + i])
                        new_header = sku_df_2.iloc[0]  # Grab the first row for the header
                        sku_df_2 = sku_df_2[1:]  # Take the data less the header row
                        sku_df_2.columns = new_header  # Set the header row as the df header
                        sku_df_2 = sku_df_2.apply(pd.to_numeric, errors='ignore')
                        sku_pt_2 = pd.pivot_table(data=sku_df_2, index="Item name",
                                                    values=["Items viewed", "Items purchased"], aggfunc="sum")
                        sku_pt_2["CR Ratio"] = (sku_pt_2["Items purchased"] / sku_pt_2["Items viewed"]).round(2)
                        sku_filtered_pt_2 = sku_pt_2[sku_pt["Items viewed"] > 100].sort_values(by="Items viewed", ascending=False)
                        st.write(sku_df_2)
                        st.write(sku_filtered_pt_2)
                        st.subheader("Comparison of Items between time periods (Absolute)")
                        sku_difference_pt = sku_filtered_pt - sku_filtered_pt_2
                        st.write(sku_difference_pt.sort_values(by="Items viewed", ascending=False))
                        sku_sourcemed_fig = go.Figure(
                            data=[
                                go.Scatter(
                                    x=sku_filtered_pt_2["Items viewed"],
                                    y=sku_filtered_pt_2.index,
                                    mode="markers",
                                    name="before",
                                    marker=dict(
                                        color="green",
                                        size=10
                                    )

                                ),
                                go.Scatter(
                                    x=sku_filtered_pt["Items viewed"],
                                    y=sku_filtered_pt.index,
                                    mode="markers",
                                    name="after",
                                    marker=dict(
                                        color="blue",
                                        size=10
                                    )
                                ),
                            ]
                        )
                        st.write(sku_sourcemed_fig)
                        st.subheader("Comparison of items viewed between time periods (%)")
                        sku_difference_p_pt = (sku_filtered_pt - sku_filtered_pt_2)/sku_filtered_pt_2
                        st.write(sku_difference_p_pt.sort_values(by="Items viewed", ascending=False))
                        st.subheader("Comparison of source/medium between time periods")
                        sku_sourcemed_option = st.selectbox(
                            'Select items', sku_filtered_pt.index)
                        sku_campaign_pt = pd.pivot_table(sku_df[sku_df["Item name"] == sku_sourcemed_option],
                                                     index="Session source / medium",
                                                     values=["Items viewed", "Items purchased"],
                                                     aggfunc="sum"
                                                     )
                        sku_campaign_pt["CR Ratio"] = sku_campaign_pt["Items purchased"] / sku_campaign_pt["Items viewed"]
                        sku_campaign_pt_2 = pd.pivot_table(sku_df_2[sku_df_2["Item name"] == sku_sourcemed_option],
                                                           index="Session source / medium",
                                                           values=["Items viewed", "Items purchased"],
                                                           aggfunc="sum"
                                                     )
                        sku_campaign_pt_2["CR Ratio"] = sku_campaign_pt_2["Items purchased"] / sku_campaign_pt_2["Items viewed"]
                        st.write(sku_campaign_pt - sku_campaign_pt_2)
