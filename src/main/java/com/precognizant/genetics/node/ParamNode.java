/*
 * @(#)ParamNode.java $Date: Feb 15, 2011 6:28:27 PM $
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

import java.util.ArrayList;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jan 29, 2011 2:23:35 AM
 */
public class ParamNode implements Node {
	private int paramNumber;

	protected ParamNode() {
		
	}
	
	public ParamNode(int param) {
		this.setParamNumber(param);
	}

	public Number getParam() {
		return getParamNumber();
	}

	public void setParam(int param) {
		this.setParamNumber(param);
	}

	/* (non-Javadoc)
	 * @see com.fortmoon.genetics.Node#evaluate(java.util.ArrayList)
	 */
	@Override
	public <T extends Node> Number evaluate(ArrayList<T> args) {
		return args.get(getParamNumber()).evaluate(args);
	}
	
	public String toString() {
		if(getParamNumber() == 0)
			return "x";
		if(getParamNumber() == 1)
			return "y";
		if(getParamNumber() == 2)
			return "z";
		if(getParamNumber() > 2)
			return "f" + (getParamNumber() + 1);

		return "IN:" + getParamNumber();
	}

	public boolean equals(Object o) {
		System.out.println("Equals called.");
		if(o instanceof ParamNode) {
			if(((ParamNode)o).getParamNumber() == this.getParamNumber()) {
				return true;
			}
		}
		return false;
	}

	public int getParamNumber() {
		return paramNumber;
	}

	public void setParamNumber(int paramNumber) {
		this.paramNumber = paramNumber;
	}
}
