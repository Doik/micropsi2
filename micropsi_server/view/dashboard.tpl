

<div id="dashboard_viewer" class="section-margin frontend_section collapse in">
    <div class="sectionbar">
        <form class="navbar-form">
            <table>
                <tr>
                    <td><span><i
                            class="icon-chevron-right"></i></span></td>

                    <td> Agent Dashboard &nbsp;</td>
                    <td>
                        <div class="btn-group nodenet_list">
                            <a class="btn" href="#">
                                (no nodenet selected)
                            </a>
                        </div>
                    </td>
                </tr>
            </table>
        </form>
    </div>

    <div id="dashboard" class="section-margin collapse in frontend_section">
        <div id="dashboard_container" class="section">
            <div class="span6">
                <div id="dashboard_urges" class="dashboard-item left"></div><div id="dashboard_valence" class="dashboard-item left"></div>
                <div id="arrow_motivation" class="arrow arrow_left dashboard-item right"></div>
                <p style="clear:both">
                <div id="arrow_modulators" class="arrow arrow_down"></div>
                <div id="dashboard_modulators" class="dashboard-item left" style="clear:both"></div><div id="dashboard_face" class="dashboard-item left"></div>
            </div>
            <div class="span3">
                <p style="clear:both"/>
                <div id="dashboard_datatable_motivation" class="dashboard-item left"></div>
                <div id="dashboard_nodes" class="dashboard-nodes left"></div>
            </div>
            <div class="span3">
                <div id="dashboard_datatable_concepts" class="dashboard-item left"></div>
            </div>
            <p style="clear:both"/>
        </div>
    </div>
    <div id="monitor" class="section-margin frontend_section collapse in">
        <div class="section multiple">
            <div class="monitor_field layout_field span6">
                <h4>Monitors</h4>
                <div class="contentbox section">
                    <div id="graph"></div>
                    <div class="monitor_seperator">
                        <form class="form-horizontal monitor_list">
                            <label for="monitor_x_axis">
                                No. of steps:
                            </label>
                            <select id="monitor_x_axis" class="input-mini">
                                <option>100</option>
                                <option>200</option>
                                <option>500</option>
                                <option>1000</option>
                                <option value="-1">all</option>
                            </select>
                        </form>
                        <ul id="monitor_selector" class="monitor_list">
                        </ul>
                    </div>
                </div>
            </div>
            <div class="logger_field layout_field span6">
                <h4>Logs</h4>
                <div class="contentbox section">
                    <div id="logs"></div>
                    <form class="form-horizontal span4 monitor_seperator">
                        <ul id="log_selector" class="monitor_list">
                            <li>
                                <label for="log_system" class="system_log">
                                    <input type="checkbox" id="log_system" class="log_switch" data="system" />
                                    System
                                </label>
                                <select id="level_log_system" class="log_level_switch" data="system">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['system'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['system'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['system'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['system'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                            <li>
                                <label for="log_world" class="world_log">
                                    <input type="checkbox" id="log_world" class="log_switch" data="world" />
                                    World
                                </label>
                                <select id="level_log_world" class="log_level_switch" data="world">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['world'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['world'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['world'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['world'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                            <li>
                                <label for="log_agent" class="agent_log">
                                    <input type="checkbox" id="log_agent" class="log_switch" data="agent" />
                                    Agent
                                </label>
                                <select id="level_log_agent" class="log_level_switch" data="agent">
                                    <option value="DEBUG" {{'selected="selected"' if logging_levels['agent'] == "DEBUG" else ""}}>Debug</option>
                                    <option value="INFO" {{'selected="selected"' if logging_levels['agent'] == "INFO" else ""}}>Info</option>
                                    <option value="WARNING" {{'selected="selected"' if logging_levels['agent'] == "WARNING" else ""}}>Warning</option>
                                    <option value="ERROR" {{'selected="selected"' if logging_levels['agent'] == "ERROR" else ""}}>Error</option>
                                </select>
                            </li>
                        </ul>
                    </form>
                    <form class="form-horizontal span4 monitor_list">
                        <label for="monitor_filter_logs">Filter:</label>
                        <input type="text" value="" id="monitor_filter_logs" class="input-small"/>
                    </form>
                </div>
            </div>
            <p style="clear:both">&nbsp;</p>
        </div>
    </div>
</div>

<script src="/static/js/d3.v2.min.js" type="text/javascript"></script>
<script src="/static/js/dashboard.js" type="text/javascript"></script>
<script src="/static/js/monitor.js" type="text/javascript"></script>
