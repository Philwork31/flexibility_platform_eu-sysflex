<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:r="http://schemas.openxmlformats.org/package/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:rD="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:sys="http://sysFlex/Lib" xmlns:m="http://schemas.openxmlformats.org/spreadsheetml/2006/main">

	

	<xsl:function as="xs:dateTime" name="sys:add-duration-to-datetime">
		<xsl:param as="xs:dateTime" name="start"/>
		<xsl:param as="xs:duration" name="duration"/>
		
		<xsl:variable name="dur" as="xs:dayTimeDuration" select="xs:dayTimeDuration( $duration )"/>
		<xsl:value-of select="$start+$dur"/>
	</xsl:function>
	
</xsl:stylesheet>