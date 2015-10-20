/*
 * @(#)Gene.java $Date: Feb 15, 2011 6:28:27 PM $
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
package com.precognizant.genetics.core;

import com.precognizant.genetics.node.Node;
import com.precognizant.genetics.node.NodeTreeImpl;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Gene {
	protected Node node;
	private static NodeTreeImpl nodeTreeImpl = new NodeTreeImpl();
	
	public Gene(int inputSize) {
		node = nodeTreeImpl.getNode(inputSize);
	}
	
	public Gene(Node node) {
		this.node = node;
	}
	
	public Node getNode() {
		return node;
	}
	
	public String toString() {
		return node.toString();
	}
}
