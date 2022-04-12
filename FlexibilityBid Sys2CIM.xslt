<?xml version="1.0" encoding="UTF-8"?>
<!--
This file was generated by Altova MapForce 2021

YOU SHOULD NOT MODIFY THIS FILE, BECAUSE IT WILL BE
OVERWRITTEN WHEN YOU RE-RUN CODE GENERATION.

Refer to the Altova MapForce Documentation for further details.
http://www.altova.com/mapforce
-->
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sys="http://sysFlex/Lib" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="sys xs fn">
	<xsl:include href="EuSysFlex_Lib.xsl"/>
	<xsl:output method="xml" encoding="UTF-8" byte-order-mark="no" indent="yes"/>
	<xsl:template match="/">
		<xsl:variable name="var2_PT_H_as_duration" as="xs:duration" select="xs:duration('PT1H')"/>
		<xsl:variable name="var1_FlexibilityBid" as="node()?" select="FlexibilityBid"/>
		<FlexibilityBid_MarketDocument xmlns="CIM/EuSysFlex/FlexibilityBid">
			<xsl:attribute name="xsi:schemaLocation" namespace="http://www.w3.org/2001/XMLSchema-instance" select="'CIM/EuSysFlex/FlexibilityBid file:///C:/Users/cyril/Downloads/EuSysFlex/CIM_flexibilityBid.xsd'"/>
			<Bid_TimeSeries xmlns="">
				<Delivery_Period>
					<Point>
						<position>
							<xsl:sequence select="xs:string(xs:integer(xs:decimal('0')))"/>
						</position>
						<Price>
							<xsl:for-each select="$var1_FlexibilityBid">
								<amount>
									<xsl:sequence select="xs:string(xs:decimal(fn:string(price)))"/>
								</amount>
							</xsl:for-each>
						</Price>
						<xsl:for-each select="$var1_FlexibilityBid">
							<quantity>
								<xsl:sequence select="xs:string(xs:decimal(fn:string(power)))"/>
							</quantity>
						</xsl:for-each>
					</Point>
					<resolution>
						<xsl:sequence select="xs:string($var2_PT_H_as_duration)"/>
					</resolution>
					<timeInterval>
						<xsl:for-each select="$var1_FlexibilityBid">
							<end>
								<xsl:sequence select="xs:string(sys:add-duration-to-datetime(xs:dateTime(fn:string(start_of_delivery)), $var2_PT_H_as_duration))"/>
							</end>
						</xsl:for-each>
						<xsl:for-each select="$var1_FlexibilityBid">
							<start>
								<xsl:sequence select="xs:string(xs:dateTime(fn:string(start_of_delivery)))"/>
							</start>
						</xsl:for-each>
					</timeInterval>
				</Delivery_Period>
				<Metering_MarketEvaluationPoint>
					<xsl:for-each select="$var1_FlexibilityBid">
						<mRID>
							<xsl:sequence select="fn:string(metering_point_id)"/>
						</mRID>
					</xsl:for-each>
				</Metering_MarketEvaluationPoint>
				<mRID>
					<xsl:sequence select="generate-id()"/>
				</mRID>
				<xsl:for-each select="$var1_FlexibilityBid">
					<product>
						<xsl:sequence select="fn:string(product_id)"/>
					</product>
				</xsl:for-each>
			</Bid_TimeSeries>
			<LocalizationFactor_Domain xmlns="">
				<xsl:for-each select="$var1_FlexibilityBid">
					<mRID>
						<xsl:sequence select="fn:string(localization_factor)"/>
					</mRID>
				</xsl:for-each>
			</LocalizationFactor_Domain>
			<xsl:for-each select="$var1_FlexibilityBid">
				<mRID xmlns="">
					<xsl:sequence select="generate-id(.)"/>
				</mRID>
			</xsl:for-each>
			<Period xmlns="">
				<timeInterval>
					<xsl:for-each select="$var1_FlexibilityBid">
						<end>
							<xsl:sequence select="xs:string(sys:add-duration-to-datetime(xs:dateTime(xs:date(xs:dateTime(fn:string(start_of_delivery)))), xs:duration('PT24H')))"/>
						</end>
					</xsl:for-each>
					<xsl:for-each select="$var1_FlexibilityBid">
						<start>
							<xsl:sequence select="xs:string(xs:dateTime(xs:date(xs:dateTime(fn:string(start_of_delivery)))))"/>
						</start>
					</xsl:for-each>
				</timeInterval>
			</Period>
			<Provider_MarketParticipant xmlns="">
				<xsl:for-each select="$var1_FlexibilityBid">
					<mRID>
						<xsl:sequence select="fn:string(flexibility_service_provider)"/>
					</mRID>
				</xsl:for-each>
			</Provider_MarketParticipant>
		</FlexibilityBid_MarketDocument>
	</xsl:template>
</xsl:stylesheet>
