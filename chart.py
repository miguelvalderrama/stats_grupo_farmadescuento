import altair as alt


def get_chart(data, title, y, tooltip_y, group, promed=False, mean=None):
    hover = alt.selection_single(
        fields=["Fecha"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title=title)
        .mark_line()
        .encode(
            x="Fecha",
            y=y,
            color=alt.Color(group,scale=alt.Scale(scheme='category10')),
            strokeDash=group
        )
    )

    if promed:
        rule = alt.Chart(data).mark_rule(color='blue').encode(
        y=mean,
        strokeWidth=alt.value(3))

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="Fecha",
            y=y,
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Fecha", title="Fecha"),
                alt.Tooltip(y, title=tooltip_y),
            ],
        )
        .add_selection(hover)
    )
    if promed:
        return (lines + points + tooltips + rule).interactive()
    return (lines + points + tooltips).interactive()