import json
import math

import plotly
import plotly.graph_objs as go


# e0 удлинение в долях, для определения предела текучести
# E = 210000


def calc_new_tube_yield(props, thickness=50, radius=280):
    sloy = 1000
    k = (1 / (math.log(1 + (thickness / radius)))) - (radius / thickness)  # коэффициент положения нейтральной линии
    x_nl = thickness * k
    s_sloy = thickness / sloy
    R_ns = radius + x_nl
    PE = []
    x_sloy = []
    for i in range(0, sloy + 1):
        x_i = i * s_sloy
        r0 = radius + x_i
        r1 = R_ns
        if x_i < x_nl:
            PE_i = ((r1 - r0) / r1) * 100
        else:
            PE_i = ((r0 - r1) / r1) * 100
        PE.append(PE_i)
        x_sloy.append(x_i)

    PE_av = sum(PE) / len(PE) / 100

    strain_t = []
    stress_t = []
    for prop in props:
        e = float(prop[0])
        sigma = float(prop[1])
        strain_t.append(e)
        stress_t.append(sigma)

    E = stress_t[1] / strain_t[1]

    PE_razgib = (PE_av * 1.7) - strain_t[1]

    new_sigma_t = identify_stress(PE_av, strain_t, stress_t)
    new_sigma_t_razgib = identify_stress(PE_razgib, strain_t, stress_t)
    graphJSON = hardening_curve(PE_av, new_sigma_t, new_sigma_t_razgib, strain_t, stress_t, strain_t[1], stress_t[1],
                                PE_razgib)

    graphJSON2 = neutral_line(PE, thickness, sloy, x_sloy)

    tubes_values = {'plot': graphJSON,
                    'sigma_t': stress_t[1],
                    'PE_avg': round(PE_av * 100, 2),
                    'PE_razgib': round(PE_razgib * 100, 2),
                    'new_sigma_t': new_sigma_t,
                    'new_sigma_t_razgib': new_sigma_t_razgib,
                    'plot2': graphJSON2,
                    'PE_min_max': [round(PE[1], 2), round(PE[-1], 2)],
                    'PE_razgib_min_max': [round((PE[1] * 1.7) - strain_t[1], 2),
                                          round((PE[-1] * 1.7) - strain_t[1], 2)],
                    }

    return tubes_values


def neutral_line(PE, thickness, sloy, x_sloy):
    pe_min = PE.index(min(PE))
    x1_x_sloy = x_sloy[:pe_min:25] + [x_sloy[pe_min]]
    y1_PE = PE[:pe_min:25] + [0]
    x2_x_sloy = x_sloy[-1:pe_min:-25] + [x_sloy[pe_min]]
    y2_PE = PE[-1:pe_min:-25] + [0]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x1_x_sloy, y=y1_PE,
                              mode='lines+markers',
                              name=f'Сжимающие',
                              hovertemplate='x = %{x} мм<br>y = %{y} %',
                              marker=dict(color='blue')
                              ))
    fig2.add_trace(go.Scatter(x=x2_x_sloy, y=y2_PE,
                              mode='lines+markers',
                              name=f'Растягивающие',
                              hovertemplate='x = %{x} мм<br>y = %{y} %',
                              marker=dict(color='red')
                              ))
    fig2.add_trace(go.Scatter(x=x_sloy[::100], y=[round(sum(PE) / len(PE), 3)] * 11,
                              mode='lines',
                              name=f'Усреднeнное по сечению<br> значение деформации',
                              hovertemplate='x = %{x} мм<br>y = %{y} %',
                              marker=dict(color='black')
                              ))
    fig2.update_xaxes(
        title_text="Толщина, мм",
        title_font={"size": 14},
        title_standoff=8)
    fig2.update_yaxes(
        title_text="Деформация, %",
        title_font={"size": 14},
        title_standoff=8)
    fig2.update_layout(template="simple_white", yaxis_range=[-0.2, max(PE) * 1.2],
                       xaxis_range=[-0.1, max(x_sloy) * 1.1],
                       dragmode=False, title={
            'text': f'Распределение накопленных деформаций по толщине после вальцовки <br>'
                    f'Положение нейтральной линии по толщине' +
                    f' - {round(x_sloy[PE.index(min(PE))], 1)}' + 'мм', },
                       legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.25), )

    # fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    # fig2.add_trace(go.Heatmap(
    #     x=PE,
    #     y=x_sloy,
    #     z=[[z] * int(thickness) for z in range(sloy)],
    #     colorscale=[[0.0, "rgb(49,54,149)"],
    #                 [x_sloy[PE.index(min(PE))] / thickness, "rgb(250,250,250)"],
    #                 [1.0, "rgb(165,0,38)"]],
    #     showscale=False,
    #     hoverinfo='none'
    # ), secondary_y=False)
    #
    # fig2.add_trace(
    #     go.Scatter(x=[PE[0], PE[-1]], y=[-PE[0], PE[-1]], name="yaxis2 data"),
    #     secondary_y=True
    # )
    # fig2.update_yaxes(title_text=_("Толщина, мм"),
    #                   title_font={"size": 14},
    #                   title_standoff=8, secondary_y=False)
    # fig2.update_xaxes(title_text=_("Внешние волокна"),
    #                   title_font={"size": 14},
    #                   showticklabels=False,
    #                   side="top")
    # fig2.update_layout(template="simple_white",
    #                    title={'text': _(f'Распределение накопленных пластических деформаций по толщине после вальцовки <br>'
    #                                     f'Положение нейтральной линии по толщине') + f' - {round(x_sloy[PE.index(min(PE))], 1)}' + _(
    #                        'мм'),
    #                           },
    #                    yaxis=dict(
    #                        tickmode='array',
    #                        tickvals=[0, round(x_sloy[PE.index(min(PE))], 1), thickness],
    #                        ticktext=[0, round(x_sloy[PE.index(min(PE))], 1), thickness]
    #                    ),
    #                    yaxis2=dict(
    #                        tickmode='array',
    #                        tickvals=[-round(PE[0], 2), round(min(PE), 1), round(PE[-1], 2)],
    #                        ticktext=[-round(PE[0], 2), round(min(PE), 1), round(PE[-1], 2)]
    #                    ),
    #                    dragmode=False,
    #                    xaxis_range=[PE[0] * 0.99, PE[0] * 0.999],
    #                    margin=dict(t=150)
    #                    )

    # fig2.update_yaxes(title_text=_("Накопленные пластические <br> деформации, %"), secondary_y=True)

    # fig2.show()

    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON2


def hardening_curve(PE_all, new_sigma_t, new_sigma_t_razgib, strain_t, stress_t, e0, sigma_t, e_razgib):
    fig = go.Figure()
    strain_t_percent = [round(x * 100, 2) for x in strain_t]
    fig.add_trace(go.Scatter(x=strain_t_percent, y=stress_t,
                             mode='lines+markers',
                             name=f'Исходная кривая упрочнения',
                             hovertemplate='x = %{x}% <br>y = %{y} МПа',
                             marker=dict(color='#5992C5')
                             ))
    fig.add_trace(go.Scatter(x=[round(e0 * 100, 3)], y=[sigma_t],
                             mode='markers',
                             name=f'Исходный предел текучести',
                             marker=dict(symbol=['x'],
                                         line_width=1,
                                         size=12,
                                         line_color="black",
                                         color="#f34b3f"),
                             hovertemplate='%{y} МПа'
                             ))
    fig.add_trace(go.Scatter(x=[round(PE_all * 100, 3)], y=[new_sigma_t],
                             mode='markers',
                             name=f'Предел текучести после деформации',
                             marker=dict(symbol=['x'],
                                         line_width=1,
                                         size=12,
                                         color="#FFCB47",
                                         line_color="black"),
                             hovertemplate='y = %{y} МПа'
                             ))
    fig.add_trace(go.Scatter(x=[round(e_razgib * 100, 3)], y=[new_sigma_t_razgib],
                             mode='markers',
                             name=f'Предел текучести после разгибки',
                             marker=dict(symbol=['x'],
                                         line_width=1,
                                         size=12,
                                         color="#58c661",
                                         line_color="black"),
                             hovertemplate='y = %{y} МПа'
                             ))
    fig.update_xaxes(
        title_text="Деформация, %",
        title_font={"size": 14},
        title_standoff=8)
    fig.update_yaxes(
        title_text="Напряжения, МПа",
        title_font={"size": 14},
        title_standoff=8)
    fig.update_layout(template="simple_white", yaxis_range=[0, max(stress_t) + 5],
                      xaxis_range=[0, max(strain_t_percent) * 1.1],
                      dragmode=False, legend=dict(yanchor="top", y=0.4, xanchor="left", x=0.3),)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # fig.show(config=fig_config)

    # Для показа в юпитере
    # f2 = go.FigureWidget(fig)
    # f2

    return graphJSON


def identify_stress(strain: float, strain_list: list, stress_list: list):
    current_strain = 0
    for i in strain_list[1::]:
        if i < strain:
            current_strain = i
        else:
            break
    index = strain_list.index(current_strain)

    current_stress = round(stress_list[index] + (
            (stress_list[index + 1] - stress_list[index]) / (strain_list[index + 1] - strain_list[index])) * (
                                   strain - strain_list[index]), 1)

    return current_stress
