<?php

# Solution for the 1st part of IPP project 2023
# VUT FIT Sergei Rasstrigin (xrasst00)

ini_set('display_errors', 'stderr');

$inst_cnt = 0;
#================== ARG PARSER ===============
$aruments_flag = check_args($argc,$argv);
if($aruments_flag == 99) exit(0);
elseif ($aruments_flag) exit(10); #param error
#=============================================

if(read_header())
{
    echo("Header error");
    exit(21);
}

#==================================================
$xml = new XMLWriter();
$xml->openMemory();
$xml->setIndent(1);
$xml->startDocument('1.0','UTF-8');


$xml->startElement('program');
$xml->writeAttribute('language',"IPPcode23");
#==================================================

parse();

$xml->endElement();
$xml->endDocument();
#======= SEND TO STDOUT ===========
fwrite(STDOUT, $xml->outputMemory());
#==================================
exit(0);
#==================================

function parse() : void
{
    global $inst_cnt;
    global $xml;
    while ($line = fgets(STDIN)) {
        if(!empty($line))
        {
            $split = explode('#', rtrim($line, "\n"));
            $split_ = preg_split('/(\s+)/', trim($split[0], "\n"), -1, PREG_SPLIT_NO_EMPTY == 1);

            if(!empty($split_[0]))
            {
                switch (strtoupper($split_[0]))
                {
                    case 'CREATEFRAME': # NOTHING
                    case 'PUSHFRAME':
                    case 'POPFRAME':
                    case 'RETURN':
                    case 'BREAK':
                        $inst_cnt += 1;
                        if(count($split_) !== 1)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));
                        $xml->endElement();

                        break;
                    case 'DEFVAR':
                    case 'POPS': # VAR
                        $inst_cnt += 1;
                        if(count($split_) !== 2)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_var($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));
                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","var");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();
                        $xml->endElement();

                        break;
                    case 'MOVE': # VAR SYMB
                    case 'INT2CHAR':
                    case 'STRLEN':
                    case 'NOT':
                    case 'TYPE':
                        $inst_cnt += 1;
                        if(count($split_) !== 3)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_var($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_symb($split_[2]) === 1) # bad
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","var");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();

                        if((strpos($split_[2],"int") === 0) || strpos($split_[2],"bool") === 0 || strpos($split_[2],"nil") === 0 || strpos($split_[2],"string") === 0)
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type",explode('@',$split_[2])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[2],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[2]));
                            $xml->endElement();
                        }

                        $xml->endElement();

                        break;
                    case 'LABEL': # LABEL ONLY
                    case 'JUMP':
                    case 'CALL':
                        $inst_cnt += 1;
                        if(count($split_) !== 2)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_label($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","label");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();

                        $xml->endElement();
                        break;
                    case 'PUSHS': # SYMB ONLY
                    case 'WRITE':
                    case 'EXIT':
                    case 'DPRINT':
                        $inst_cnt += 1;
                        if(count($split_) !== 2)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_symb($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        if((strpos($split_[1],"int") === 0) || strpos($split_[1],"bool") === 0 || strpos($split_[1],"nil") === 0 || strpos($split_[1],"string") === 0)
                        {
                            $xml->startElement("arg1");
                            $xml->writeAttribute("type",explode('@',$split_[1])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[1],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg1");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[1]));
                            $xml->endElement();
                        }

                        $xml->endElement();
                        break;
                    case 'ADD': #VAR SYMB SYMB
                    case 'SUB':
                    case 'MUL':
                    case 'IDIV':
                    case 'LT':
                    case 'GT':
                    case 'EQ':
                    case 'AND':
                    case 'OR':
                    case 'STRI2INT':
                    case 'CONCAT':
                    case 'GETCHAR':
                    case 'SETCHAR':
                        $inst_cnt += 1;
                        if(count($split_) !== 4)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_var($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_symb($split_[2]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_symb($split_[3]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","var");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();

                        if((strpos($split_[2],"int") === 0) || strpos($split_[2],"bool") === 0 || strpos($split_[2],"nil") === 0 || strpos($split_[2],"string") === 0)
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type",explode('@',$split_[2])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[2],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[2]));
                            $xml->endElement();
                        }

                        if((strpos($split_[3],"int") === 0) || strpos($split_[3],"bool") === 0 || strpos($split_[3],"nil") === 0 || strpos($split_[3],"string") === 0)
                        {
                            $xml->startElement("arg3");
                            $xml->writeAttribute("type",explode('@',$split_[3])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[3],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg3");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[3]));
                            $xml->endElement();
                        }

                        $xml->endElement();

                        break;
                    case 'READ': #VAR TYPE
                        $inst_cnt += 1;
                        if(count($split_) !== 3)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_var($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_type($split_[2]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","var");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();

                        $xml->startElement("arg2");
                        $xml->writeAttribute("type","type");
                        $xml->writeRaw("$split_[2]");
                        $xml->endElement();

                        $xml->endElement();
                        break;
                    case 'JUMPIFEQ': # LABEL SYMB SYMB
                    case 'JUMPIFNEQ':
                        $inst_cnt += 1;

                        if(count($split_) !== 4)
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif(check_label($split_[1]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_symb($split_[2]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }
                        elseif (check_symb($split_[3]))
                        {
                            echo("lexical or syntactic error");
                            exit(23);
                        }

                        $xml->startElement("instruction");
                        $xml->writeAttribute("order",$inst_cnt);
                        $xml->writeAttribute("opcode",strtoupper($split_[0]));

                        $xml->startElement("arg1");
                        $xml->writeAttribute("type","label");
                        $xml->writeRaw(string_replace($split_[1]));
                        $xml->endElement();


                        if((strpos($split_[2],"int") === 0) || strpos($split_[2],"bool") === 0 || strpos($split_[2],"nil") === 0 || strpos($split_[2],"string") === 0)
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type",explode('@',$split_[2])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[2],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg2");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[2]));
                            $xml->endElement();
                        }

                        if((strpos($split_[3],"int") === 0) || strpos($split_[3],"bool") === 0 || strpos($split_[3],"nil") === 0 || strpos($split_[3],"string") === 0)
                        {
                            $xml->startElement("arg3");
                            $xml->writeAttribute("type",explode('@',$split_[3])[0]);
                            $xml->writeRaw(string_replace(explode('@',$split_[3],2)[1]));
                            $xml->endElement();
                        }
                        else
                        {
                            $xml->startElement("arg3");
                            $xml->writeAttribute("type","var");
                            $xml->writeRaw(string_replace($split_[3]));
                            $xml->endElement();
                        }

                            $xml->endElement();
                            break;

                    default:
                        echo("Unexpected opcode!" . $split_[0]);
                        exit(22);
                }

            }

        }

    }
}

function check_args($argc, $argv) : int{
    if($argc > 2) return 1;
    if($argc == 2)
    {
        if($argv[1] == "--help")
        {
            echo("parse.php can work only with 0 or 1 parameter \"--help\" \n");
            echo("Exit codes: \n");
            echo("21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode23\n");
            echo("22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode23\n");
            echo("23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode23\n");
            echo("INPUT - STDIN | OUTPUT - STDOUT(XML format)\n");
            return 99;
        }
        else
        {
            echo("Param error");
            return 1;
        }

    }
    return 0;
}

function read_header() : int
{
    $my_head = ".IPPcode23";
    while($header = fgets(STDIN))
    {
        if(!empty($header))
        {
            $split = explode('#', rtrim($header, "\n"));
            $split_ = preg_split('/(\s+)/', rtrim($split[0], "\n"), -1, PREG_SPLIT_NO_EMPTY == 1);

            if (!empty($split_[0]))
            {
                if ($split_[0] === $my_head)
                {
                    return count($split_) == 1 ? 0 : 1;
                }
                else
                {
                    return 1;
                }
            }
        }


    }

    return 1;
}

function check_var($variable) : int
{
    #var regex "/(LF|GF|TF)@[a-zA-Z#&*$_\-%!?][a-zA_Z#&*$\-_%!?0-9]*/"
    if(preg_match("/^(LF|GF|TF)@[a-zA-Z#&*$\-_%!?][a-zA-Z#&*$\-_%!?0-9]*$/",$variable))
    {
        return 0;
    }
    #echo($variable);
    return 1;
}

function check_symb($symb) : int
{
    #symb regex string [a-zA-Z0-9á-žÁ-Ž\x{00}-\x{7F}]
    # or [\p{L}\p{N}\p{M}\p{P}\p{S}\p{Z}\x{00}-\x{7F}]

    if(preg_match("/^int@[+-]?[0-9]+$/",$symb) ||
        preg_match("/^bool@(true|false)$/",$symb) ||
        preg_match("/^string@[a-zA-Z0-9á-žÁ-Ž\x{00}-\x{7F}\p{L}\p{N}\p{M}\p{P}\p{S}\p{Z}]*$/",$symb) ||
        preg_match("/^nil@nil$/",$symb) )
    {
        return 0;
    }
    elseif(!check_var($symb))
    {
        return 0;
    }
    return 1;
}

function check_type($type) : int
{
    if(preg_match("/^(int|bool|string|nil)$/", $type))
    {
        return 0;
    }
    return 1;
}

function check_label($label) : int
{
    #label regex
    if((preg_match("/^[a-zA-Z#&*$\-_%!?][a-zA-Z#&*$\-_%!?0-9]*$/", $label)))
    {
        return 0;
    }
    return 1;
}

function string_replace($string) : string
{
    $my_string = str_replace("&","&amp;",$string);
    $my_string = str_replace("<","&lt;",$my_string);
    $my_string = str_replace(">","&gt;",$my_string);
    return $my_string;

}

