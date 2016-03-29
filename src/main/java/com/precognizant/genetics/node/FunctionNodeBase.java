/*
  * @(#)FunctionNodeBase.java $Date: Feb 15, 2011 6:28:27 PM $
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
 * @since Jan 30, 2011 11:01:34 AM
 */
public class FunctionNodeBase extends FunctionNode {

	/**
	 * @param operand
	 * @param paramList
	 */
	public <T extends Node> FunctionNodeBase(Operand operand, ArrayList<T> paramList) {
		super(operand, paramList);
	}

	/* (non-Javadoc)
	 * @see com.fortmoon.genetics.Node#evaluate(java.util.ArrayList)
	 */
	@Override
	public <T extends Node> Number evaluate(ArrayList<T> args) {

		Number evaluation = operand.evaluate(paramList.get(0).evaluate(args), paramList.get(1).evaluate(args));
		return evaluation;
//		return operand.evaluate(args);
	}

}
