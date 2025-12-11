import numpy as np
import pandas as pd
from bokeh.layouts import row
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, NumeralTickFormatter, CustomJS, TapTool, HBar
from bokeh.embed import components
from datetime import datetime

from bokeh.transform import factor_cmap, cumsum


def generate_monthly_revenue_bokeh_chart(data_dicts):
    if not data_dicts:
        p = figure(height=350, width=800, title="Немає даних для відображення",
                   x_axis_label="Дата", y_axis_label="Дохід ($)")
        return components(p)

    df = pd.DataFrame(data_dicts)
    df['order_date'] = df.apply(
        lambda row: datetime(row['order_year'], row['order_month'], 1),
        axis=1
    )
    df['total_revenue'] = pd.to_numeric(df['total_revenue'])

    source = ColumnDataSource(df)

    p = figure(
        height=400,
        width=1000,
        title="Динаміка Місячного Доходу",
        x_axis_label="Дата",
        y_axis_label="Дохід ($)",
        x_axis_type="datetime",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover"
    )

    p.line(
        x='order_date',
        y='total_revenue',
        source=source,
        line_width=3,
        line_color="#00bcd4",
        legend_label="Місячний Дохід"
    )
    p.circle(
        x='order_date',
        y='total_revenue',
        source=source,
        size=8,
        color="#00796b",
        fill_alpha=0.6,
        hover_fill_color="red"
    )

    p.xaxis.formatter = DatetimeTickFormatter(months="%b %Y")

    p.yaxis.formatter = NumeralTickFormatter(format="$0,0.00")

    p.title.align = "center"
    p.toolbar.autohide = True

    script, div = components(p)
    return script, div


def generate_genre_playtime_bokeh_chart(data_dicts):
    if not data_dicts:
        p = figure(height=350, width=800, title="Немає даних для відображення",
                   x_axis_label="Середній час гри (годин)", y_axis_label="Жанр")
        return components(p)

    df = pd.DataFrame(data_dicts)
    df['avg_playtime_per_copy'] = pd.to_numeric(df['avg_playtime_per_copy'])
    df['name'] = df['name'].astype(str)

    df = df.sort_values(by='avg_playtime_per_copy', ascending=True)

    genre_list = df['name'].tolist()

    source = ColumnDataSource(df)

    p = figure(
        y_range=genre_list,
        height=450,
        width=1000,
        title="ТОП Жанрів за Середнім Часом Гри",
        x_axis_label="Середній Час Гри (годин)",
        y_axis_label="Жанр",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover"
    )

    p.hbar(
        y='name',
        right='avg_playtime_per_copy',
        height=0.8,
        source=source,
        fill_color=factor_cmap('name', palette=Category20[len(genre_list) if len(genre_list) <= 20 else 20],
                               factors=genre_list),
        line_color='white',
        legend_label="Середній Час Гри"
    )

    p.title.align = "center"
    p.toolbar.autohide = True

    p.yaxis.major_label_orientation = 0.8
    p.xgrid.grid_line_color = None

    p.xaxis.formatter = NumeralTickFormatter(format="0.00")

    script, div = components(p)
    return script, div


def generate_developer_revenue_bokeh_chart(data_dicts):
    from bokeh.layouts import column
    from bokeh.models import DataTable, TableColumn, StringFormatter, NumberFormatter

    if not data_dicts:
        empty_p = figure(height=200, width=800, title="Немає даних для відображення")
        return components(empty_p)

    df = pd.DataFrame(data_dicts)
    df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce')
    df['total_copies_sold'] = pd.to_numeric(df['total_copies_sold'], errors='coerce')
    df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')
    df['name'] = df['name'].astype(str)

    df = df.sort_values(by='total_revenue', ascending=True)
    developer_list = df['name'].tolist()

    source = ColumnDataSource(df)

    p = figure(
        y_range=developer_list,
        height=400,
        width=1000,
        title=f"ТОП {len(df)} Розробників за Загальним Доходом",
        x_axis_label="Загальний Дохід ($)",
        y_axis_label="Розробник",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover",
        tooltips=[
            ("Розробник", "@name"),
            ("Дохід", "@total_revenue{$0,0.00}"),
            ("Копій продано", "@total_copies_sold{0,0}"),
            ("Середня ціна", "@avg_price{$0,0.00}")
        ]
    )

    p.hbar(
        y='name',
        right='total_revenue',
        height=0.7,
        source=source,
        fill_color=factor_cmap('name',
                               palette=Category20[len(developer_list) if len(developer_list) <= 20 else 20],
                               factors=developer_list),
        line_color='white',
        legend_label="Дохід"
    )

    p.title.align = "center"
    p.toolbar.autohide = True
    p.yaxis.major_label_orientation = 0.8
    p.xgrid.grid_line_color = None
    p.xaxis.formatter = NumeralTickFormatter(format="$0,0.00")

    columns = [
        TableColumn(field="name", title="Розробник",
                    width=250, formatter=StringFormatter(font_style="bold")),
        TableColumn(field="total_revenue", title="Дохід ($)", width=150,
                    formatter=NumberFormatter(format="$0,0.00", text_align="right")),
        TableColumn(field="total_copies_sold", title="Копій продано", width=120,
                    formatter=NumberFormatter(format="0,0", text_align="right")),
        TableColumn(field="avg_price", title="Середня ціна", width=150,
                    formatter=NumberFormatter(format="$0,0.00", text_align="right"))
    ]

    data_table = DataTable(
        source=source,
        columns=columns,
        width=1000,
        height=250,
        editable=False,
        sortable=True,
        selectable="checkbox",
        index_position=None,
        autosize_mode="none",
        fit_columns=False
    )

    layout = column(p, data_table)
    script, div = components(layout)
    return script, div

def generate_top_rated_games_bokeh_charts(data_dicts, top_n=None):
    from bokeh.layouts import row

    if not data_dicts:
        p1 = figure(height=400, width=500, title="Немає даних для рейтингів")
        p2 = figure(height=400, width=400, title="Немає даних для цінового розподілу")
        return components(row(p1, p2))

    if top_n is None:
        top_n = 10

    df = pd.DataFrame(data_dicts)
    df['avg_rating'] = pd.to_numeric(df['avg_rating'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['title'] = df['title'].astype(str)

    df = df.sort_values(by='avg_rating', ascending=True)
    df = df.tail(top_n)

    game_list = df['title'].tolist()
    source = ColumnDataSource(df)

    p1 = figure(
        y_range=game_list,
        height=600,
        width=600,
        title=f"ТОП {top_n} Ігор за Середнім Рейтингом",
        x_axis_label="Середній Рейтинг (від 0 до 5)",
        y_axis_label="Назва Гри",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover",
        tooltips=[("Гра", "@title"), ("Рейтинг", "@avg_rating{0.00}"), ("Ціна", "@price{$0,0.00}")]
    )

    p1.hbar(
        y='title',
        right='avg_rating',
        height=0.7,
        source=source,
        fill_color=factor_cmap('title',
                               palette=Category20[len(game_list) if len(game_list) <= 20 else 20],
                               factors=game_list),
        line_color='white',
        legend_label="Рейтинг"
    )

    p1.vspan(
        x=4.0,
        line_width=2,
        line_color='red',
        line_dash='dashed',
        legend_label="Високий Рейтинг (≥4.0)"
    )

    p1.title.align = "center"
    p1.toolbar.autohide = True
    p1.x_range.end = 5.0
    p1.xaxis.formatter = NumeralTickFormatter(format="0.0")
    p1.yaxis.major_label_orientation = 0.8

    price_categories = {
        'Безкоштовні ($0.00)': (df['price'] == 0).sum(),
        'Дешеві (до $25.00)': ((df['price'] > 0) & (df['price'] <= 25)).sum(),
        'Середні ($25.01-$50.00)': ((df['price'] > 25) & (df['price'] <= 50)).sum(),
        'Дорогі (>$50.00)': (df['price'] > 50).sum()
    }

    categories = []
    values = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

    for (label, value) in price_categories.items():
        if value > 0:
            categories.append(label)
            values.append(value)

    if not values:
        p2 = figure(height=400, width=400,
                    title=f"Ціновий Розподіл (Топ-{top_n})",
                    toolbar_location=None)
        p2.title.text = "Немає даних для цінового розподілу"
        p2.title.align = "center"
    else:
        total = sum(values)
        angles = [value / total * 2 * np.pi for value in values]
        start_angles = np.cumsum([0] + angles[:-1])
        end_angles = np.cumsum(angles)
        percentages = [(value / total * 100) for value in values]

        source_pie = ColumnDataSource(data=dict(
            categories=categories,
            values=values,
            colors=colors[:len(categories)],
            start=start_angles,
            end=end_angles,
            percent=percentages
        ))

        p2 = figure(height=400, width=400,
                    title=f"Ціновий Розподіл (Топ-{top_n})",
                    toolbar_location=None,
                    tools="hover",
                    tooltips="@categories: @values ігор (@percent{0.1}%)",
                    x_range=(-0.5, 1.0))

        p2.wedge(x=0, y=1, radius=0.35,
                 start_angle='start',
                 end_angle='end',
                 line_color="white",
                 fill_color='colors',
                 legend_field='categories',
                 source=source_pie)

        p2.axis.visible = False
        p2.grid.grid_line_color = None
        p2.title.align = "center"
        p2.legend.location = "top_left"
        p2.legend.background_fill_alpha = 0.7

    layout = row(p1, p2)
    script, div = components(layout)
    return script, div

def generate_whales_analysis_bokeh_charts(rank_data_dicts, initial_genre_breakdown_data_dicts):
    if not rank_data_dicts:
        p_rank = figure(title="Немає даних користувачів для відображення", height=500, width=500)
        p_genre = figure(title="Жанровий розподіл", height=500, width=500)
        return components(row(p_rank, p_genre))

    df_rank = pd.DataFrame(rank_data_dicts)
    df_rank['total_spent'] = pd.to_numeric(df_rank['total_spent'])
    df_rank['username'] = df_rank['username'].astype(str)
    df_rank = df_rank.sort_values(by='total_spent', ascending=True)

    user_list = df_rank['username'].tolist()
    rank_source = ColumnDataSource(df_rank)

    df_genre_initial = pd.DataFrame(initial_genre_breakdown_data_dicts)

    if not df_genre_initial.empty:
        df_genre_initial['spent_on_genre'] = pd.to_numeric(df_genre_initial['spent_on_genre'])
        total_spent = df_genre_initial['spent_on_genre'].sum()
        df_genre_initial['angle'] = df_genre_initial['spent_on_genre'] / total_spent * 2 * np.pi
        df_genre_initial['color'] = Category20[len(df_genre_initial) if len(df_genre_initial) <= 20 else 20]
        df_genre_initial['percentage'] = (df_genre_initial['spent_on_genre'] / total_spent) * 100
        genre_source = ColumnDataSource(df_genre_initial)
    else:
        genre_source = ColumnDataSource(
            data={'genre_name': ["Немає даних"], 'spent_on_genre': [1], 'angle': [2 * np.pi], 'color': ['gray'],
                  'percentage': [100]})

    p_rank = figure(
        y_range=user_list, height=500, width=500,
        title="ТОП Користувачів за Витратами (Оберіть для розподілу)",
        x_axis_label="Витрачено ($)", tools="pan,wheel_zoom,box_zoom,reset,hover,save",
        tooltips=[("Користувач", "@username"), ("Витрати", "@total_spent{$0,0.00}"), ("ID", "@id")]
    )

    rank_bar = p_rank.hbar(y='username', right='total_spent', height=0.7, source=rank_source,
                           line_color='white', fill_color="#00bcd4")

    p_rank.add_tools(TapTool(renderers=[rank_bar]))
    p_rank.xaxis.formatter = NumeralTickFormatter(format="$0,0")
    p_rank.xgrid.grid_line_color = None

    p_genre = figure(
        height=500, width=500,
        title="Жанровий Розподіл Витрат (Загальний ТОП N)",
        tools="hover", tooltips="@genre_name: @spent_on_genre{$0,0.00} (@percentage{0.0}%)",
        x_range=(-0.5, 1.0)
    )

    p_genre.wedge(x=0, y=1, radius=0.4,
                  start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                  line_color="white", fill_color='color', legend_field="genre_name", source=genre_source)

    p_genre.axis.visible = False
    p_genre.grid.grid_line_color = None
    p_genre.title.align = "center"

    AJAX_PATH = "/api/analysis/user-genre-breakdown/";
    js_genre_colors = list(Category20[20])

    callback_code = f"""
        const indices = rank_source.selected.indices;
        const p_genre_title = p_genre.title;
        const genre_colors = {js_genre_colors}; 
        const ajax_path = '{AJAX_PATH}';

        if (indices.length === 0) {{
            p_genre_title.text = "Жанровий Розподіл Витрат (Загальний ТОП N)";
            return; 
        }}

        const user_id = rank_source.data['id'][indices[0]];
        const username = rank_source.data['username'][indices[0]]; 

        p_genre_title.text = `Завантаження даних для ${{username}}...`; 

        const fetch_url = ajax_path + '?user_ids=' + user_id;
        console.log("Bokeh AJAX: Запит до:", fetch_url); 
        console.log("Bokeh AJAX: Користувач ID:", user_id);


        fetch(fetch_url)
            .then(response => {{
                console.log("Bokeh AJAX: HTTP Status:", response.status);
                if (!response.ok) {{
                    throw new Error(`HTTP Error! Status: ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(data => {{
                console.log("Bokeh AJAX: Отримані дані:", data);

                let new_data = {{
                    spent_on_genre: [],
                    genre_name: [],
                    angle: [],
                    color: [],
                    percentage: []
                }};

                if (data && data.length > 0) {{
                    let total = data.reduce((sum, item) => sum + parseFloat(item.spent_on_genre), 0);

                    data.forEach((item, i) => {{
                        const spent = parseFloat(item.spent_on_genre);
                        new_data.genre_name.push(item.genre_name);
                        new_data.spent_on_genre.push(spent);
                        new_data.angle.push((spent / total) * 2 * Math.PI); 
                        new_data.color.push(genre_colors[i % genre_colors.length]);
                        new_data.percentage.push((spent / total) * 100);
                    }});

                    p_genre_title.text = `Жанровий Розподіл Витрат: ${{username}}`;
                }} else {{
                    new_data.genre_name.push("Немає витрат у вибраний період");
                    new_data.spent_on_genre.push(1);
                    new_data.angle.push(2 * Math.PI);
                    new_data.color.push("gray");
                    new_data.percentage.push(100);
                    p_genre_title.text = `Жанровий Розподіл Витрат: ${{username}} (Пусто)`;
                }}

                pie_source.data = new_data;
                pie_source.change.emit(); 
            }})
            .catch(error => {{
                console.error("Bokeh AJAX: Критична помилка обробки:", error);
                p_genre_title.text = `Помилка завантаження для ${{username}} (Див. Консоль)`; 
            }});
    """

    callback = CustomJS(args=dict(rank_source=rank_source, pie_source=genre_source, p_genre=p_genre),
                        code=callback_code)

    rank_source.selected.js_on_change('indices', callback)

    layout = row(p_rank, p_genre)
    script, div = components(layout)
    return script, div


def generate_user_activity_bokeh_charts(activity_data_dicts, correlation_value):
    if not activity_data_dicts:
        p_scatter = figure(title="Немає даних користувачів для відображення", height=600, width=800)
        return components(p_scatter)

    df = pd.DataFrame(activity_data_dicts)
    df['total_playtime'] = pd.to_numeric(df['total_playtime'], errors='coerce')
    df['games_owned'] = pd.to_numeric(df['games_owned'], errors='coerce')
    df.dropna(inplace=True)

    source = ColumnDataSource(df)

    corr_text = f"Кореляція (R): {correlation_value}" if correlation_value is not None else "Кореляція: Недоступна"
    title_text = f"Активність Користувачів: Час Гри vs. Кількість Ігор | {corr_text}"

    p_scatter = figure(
        height=600, width=800,
        title=title_text,
        x_axis_label="Кількість придбаних ігор (шт.)",
        y_axis_label="Загальний час гри (годин)",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover",
        tooltips=[
            ("Користувач", "@username"),
            ("Ігор придбано", "@games_owned"),
            ("Загальний час гри", "@total_playtime{0,0.0} год"),
            ("Середній час гри", "@avg_playtime_per_game{0.0} год")
        ]
    )

    p_scatter.circle(
        x='games_owned',
        y='total_playtime',
        source=source,
        size=10,
        color="#F4511E",
        alpha=0.6,
        hover_color="#00838F",
        hover_alpha=0.8
    )
    p_scatter.xaxis.formatter = NumeralTickFormatter(format="0")
    p_scatter.yaxis.formatter = NumeralTickFormatter(format="0,0")

    if not df.empty and correlation_value is not None:
        m, b = np.polyfit(df['games_owned'], df['total_playtime'], 1)
        df['trend'] = m * df['games_owned'] + b

        p_scatter.line(
            x='games_owned',
            y='trend',
            source=source,
            line_width=2,
            color="#00838F",
            legend_label=f"Тренд (y = {m:.2f}x + {b:.2f})"
        )
        p_scatter.legend.location = "top_left"
        p_scatter.legend.background_fill_alpha = 0.8

    script, div = components(p_scatter)
    return script, div