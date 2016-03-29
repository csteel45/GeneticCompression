/*
 * @(#)ConstNode.java $Date: Feb 15, 2011 6:28:27 PM $
 * 
 * Copyright 2011 FortMoon Consulting, Inc. All Rights Reserved.
 * 
 * This software is the confidential and proprietary information of FortMoon
 * Consulting, Inc. ("Confidential Information"). You shall not disclose such
 * Confidential Information and shall use it only in accordance with the terms
 * of the license agreement you entered into with FortMoon Consulting.
 * 
 * FORTMOON MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
 * NON-INFRINGEMENT. FORTMOON SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY
 * LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES.
 * 
 */
package com.precognizant.genetics.node;

import java.math.BigDecimal;
import java.util.ArrayList;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 2:22:40 AM
 */
public class ConstNode extends ParamNode {
	protected Number constant;

	/**
	 * @param number
	 */
	public ConstNode(Number number) {
		this.constant = number;
	}

	public Object getConstant() {
		return constant;
	}

	public void setConstant(Number constant) {
		this.constant = constant;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see com.fortmoon.genetics.Node#evaluate(java.util.ArrayList)
	 */
	@Override
	public <T extends Node> Number evaluate(ArrayList<T> args) {
		return constant;
	}

	public String toString() {
		if (constant instanceof Integer)
			return ((Integer) constant).toString();
		if (constant instanceof Long)
			return ((Long) constant).toString();
		if (constant instanceof Float)
			return ((Float) constant).toString();
		if (constant instanceof Double)
			return ((Double) constant).toString();
		if (constant instanceof BigDecimal)
			return ((BigDecimal) constant).toString();

		return new String("Unknown number type: " + constant);
	}
}
