<?xml version='1.0' encoding='UTF-8'?>
<sld:StyledLayerDescriptor xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:gml='http://www.opengis.net/gml' xmlns:ogc='http://www.opengis.net/ogc' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' version='1.0.0' xsi:schemaLocation='http://www.opengis.net/sld StyledLayerDescriptor.xsd' xmlns:sld='http://www.opengis.net/sld' >
    <sld:NamedLayer>
        <sld:Name><![CDATA[{{ name }}]]> Flood Road</sld:Name>
            <sld:UserStyle>
                <sld:FeatureTypeStyle>
{% for scale_key,scale_value in scales.items %}
   {% for class_key,class_value in classifications.items %}
       {% for symbol_key,symbol_value in symbols.items %}
                    <sld:Rule>
                        <sld:Name><![CDATA[> {{ class_key }} meters of water]]></sld:Name>
                        <sld:Title><![CDATA[> {{ class_key }} meters of water]]]></sld:Title>
                        <ogc:Filter>
                            <ogc:And>
                                {% if symbol_field %}
                                <ogc:PropertyIsEqualTo>
                                    <ogc:PropertyName>{{ symbol_field }}</ogc:PropertyName>
                                    <ogc:Literal><![CDATA[{{ symbol_key }}]]></ogc:Literal>
                                </ogc:PropertyIsEqualTo>
                                {% endif %}
                                <ogc:PropertyIsGreaterThanOrEqualTo>
                                    <ogc:PropertyName>{{ damage_field }}</ogc:PropertyName>
                                    <ogc:Literal>{{ class_value.min }}</ogc:Literal>
                                </ogc:PropertyIsGreaterThanOrEqualTo>
                                <ogc:PropertyIsLessThan>
                                    <ogc:PropertyName>{{ damage_field }}</ogc:PropertyName>
                                    <ogc:Literal>{{ class_value.max }}</ogc:Literal>
                                </ogc:PropertyIsLessThan>
                            </ogc:And>
                        </ogc:Filter>
                        <sld:MaxScaleDenominator>{{ scale_key }}</sld:MaxScaleDenominator>
                        <sld:PointSymbolizer>
                            <sld:Graphic>
                                <sld:Mark>
                                    <sld:WellKnownName>{{ symbol_value }}</sld:WellKnownName>
                                    <sld:Fill>
                                        <sld:CssParameter name='fill' >{{ class_value.color }}</sld:CssParameter>
                                        <sld:CssParameter name='fill-opacity' >{{ class_value.opacity }}</sld:CssParameter>
                                    </sld:Fill>
                                </sld:Mark>
                                <sld:Size>{{ scale_value }}</sld:Size>
                            </sld:Graphic>
                        </sld:PointSymbolizer>
                    </sld:Rule>
        {% endfor %}
    {% endfor %}
{% endfor %}
                </sld:FeatureTypeStyle>
            </sld:UserStyle>
    </sld:NamedLayer>
</sld:StyledLayerDescriptor>
