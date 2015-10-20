/*
 * @(#)FunctionNode.java $Date: Feb 15, 2011 6:28:27 PM $
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

import com.precognizant.genetics.operand.Operand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jan 29, 2011 2:44:49 AM
 */
public abstract class FunctionNode implements Node {
	protected Operand operand;
	protected ArrayList<Node> paramList;
	
	@SuppressWarnings("unchecked")
	public <T extends Node> FunctionNode(Operand operand, ArrayList<T> paramList2) {
		this.operand = operand;
		this.paramList = (ArrayList<Node>) paramList2;
	}
	
	public Number evaluate() {
		return operand.evaluate(paramList);
	}
	
	public String toString() {
		return operand.toString() + "(" + paramList.toString() + ")";
	}

	/**
	 * @param args
	 * @return
	 */
	public  <T extends Node> Number evaluate(ArrayList<T> args) {
		return operand.evaluate(paramList);
	}
	
	public Operand getOperand() {
		return operand;
	}
	
	public ArrayList<Node> getParamList() {
		return paramList;
	}
	
}
